from ..preprocessing._preprocessing import Preprocessor
from ._DAG import DAG, ColumnNode, PreProcesserNode,_parse_input_columns
from ._plotter import plot_dag_pipeline
from ._serializer import _serialize, _read_from_serialized
from._utils import bcolors, execute_query
import teradataml as tdml
from ..statistics.collector import collect_statistics_by_requirements
from ..sql import get_template
from string import Template
import json
from ..autoprep._builder import _get_auto_steps

class Pipeline:
    """
    A class representing a data processing pipeline, consisting of a sequence of steps, where each step
    is a tuple of input columns, preprocessors and options. During fitting, a DAG (directed acyclic graph is generated).

    Parameters
    ----------
    steps : list
        A list of tuples representing the steps of the pipeline. Each tuple must have 2 or 3 elements.
        The first element is the input columns, which can be a string, a list of strings or a dictionary.
            If it is a string, it represents a single column. If it is a list, it represents a list of column names.
            If it is a dictionary, it can have the keys 'prefix', 'suffix', 'pattern', 'dtype_include', 'dtype_exclude',
                and/or 'columns_exclude'. The value of each key must be a string or a list of strings. These key-value
                pairs will be used to get all matching columns from the current step
        The second element is the preprocessors, which can be either a single Preprocessor object or a list
            of Preprocessor objects.
        The third element is optional and contains options for the step. It is a dictionary that can have the
            keys 'prefix' and/or 'suffix', with string values. The strings will be added at the beginning or the end of
            the output column names

        Note that changing the output column names with a certain prefix/suffix makes it easier to get the column names
            for as subsequent processing steps, in particular if you have no full control over the naming (e.g. after
            applying PCA)

        Examples of valid steps:
        - (input_col, preprocessor)
        - (input_cols_list, preprocessor)
        - (input_col_dict, preprocessor)
        - (input_col, preprocessor, options_dict)
        - (input_cols_list, [preprocessor1, preprocessor2], options_dict)

    """
    def __init__(self, steps):

        self.steps = self._check_and_reformat_steps(steps)

        self._dag = None
        self._is_fitted = False
        self._fit_df = None
        self._needs_DF_for_fitting = self._check_steps_if_statistics_needed() # not used so far
        self._query = None

    def _check_and_reformat_steps(self, steps):
        assert isinstance(steps, list)
        new_steps = []
        for i, step in enumerate(steps):
            assert isinstance(step, tuple)
            assert len(step) in [2,3]
            input_columns = step[0]
            preprocessors = step[1]
            options = {}
            if len(step) ==3:
                options = step[2]

            ## input columns:
            assert isinstance(input_columns, (str, list, dict))
            if isinstance(input_columns, list):
                assert all([isinstance(col, str) for col in input_columns])
                assert len(input_columns) == len(set(input_columns))
            if isinstance(input_columns,dict):
                assert all([(k in ["prefix", "suffix", "pattern", "dtype_include", "dtype_exclude","columns_exclude"])
                            for k in input_columns.keys()])
                for key, val in input_columns.items():
                    if key in ["prefix", "suffix", "pattern"]:
                        assert isinstance(val, str)
                    elif key in ["dtype_include", "dtype_exclude", "columns_exclude"]:
                        assert isinstance(val, list) and all([isinstance(tdtype, str) for tdtype in val])
            if isinstance(input_columns, str):
                input_columns = [input_columns]



            ## preprocessors
            assert isinstance(preprocessors, (list, Preprocessor))
            if isinstance(preprocessors, list):
                assert all([isinstance(preproc, Preprocessor) for preproc in preprocessors])

            ## options
            assert all([(k in ["prefix", "suffix"])
                        for k in options.keys()])
            for key, val in options.items():
                if key in ["prefix", "suffix",]:
                    assert isinstance(val, str)


            if isinstance(preprocessors, list):
                preprop_steps_exploded = []
                if options  == {}:
                    preprop_steps_exploded = [
                        (input_columns, p, options) for p in preprocessors
                    ]
                else:
                    # step 1 stays the same
                    preprop_steps_exploded.append(((input_columns, preprocessors[0], options)))
                    # step 2 needs to change
                    prefix = options.get("prefix","")
                    suffix = options.get("suffix","")

                    if isinstance(input_columns, str):
                        changed_input_columns = prefix + input_columns + suffix
                    elif isinstance(input_columns, list):
                        changed_input_columns =  [prefix + c + suffix for c in input_columns]
                    elif isinstance(input_columns, dict):
                        if "pattern" in input_columns.keys():
                            input_columns = input_columns.copy()
                            del input_columns["pattern"]
                        current_prefix = input_columns.get("prefix","")
                        current_suffix = input_columns.get("suffix","")
                        combined_prefix = prefix + current_prefix
                        combined_suffix = current_suffix + suffix
                        changed_input_columns = input_columns.copy()
                        if len(combined_prefix)>0:
                            changed_input_columns['prefix'] = combined_prefix
                        if len(combined_suffix)>0:
                            changed_input_columns['suffix'] = combined_suffix

                    for p in preprocessors[1:]:
                        preprop_steps_exploded.append(
                            (changed_input_columns ,p,{})
                        )

                new_steps += preprop_steps_exploded


            else:
                new_steps.append((input_columns,preprocessors,options))

        return new_steps

    def _check_steps_if_statistics_needed(self):
        for step in self.steps:
            preprocessor = step[1]
            if preprocessor.define_necessary_statistics() == []:
                continue
            else:
                return True

        return False

    def _add_step_to_dag(self,  step, step_no):

        input_columns, preprocessor, options = step

        current_leaf_nodes = self._dag.get_leaf_nodes()

        relevant_nodes = _parse_input_columns(input_columns,  current_leaf_nodes)


        # Generate NEW PREPROCESSOR NODE
        pp_nodes  = []
        if preprocessor.are_inputs_combined():
            # exactly 1 node needed
            pp_nodes = [PreProcesserNode(preprocessor, step_no, options, first_node_with_preprocessor=True)]
        else:
            # as many nodes as there are input nodes
            pp_nodes += [PreProcesserNode(preprocessor, step_no, options, first_node_with_preprocessor=True)]
            pp_nodes += [PreProcesserNode(preprocessor, step_no, options) for _ in relevant_nodes[1:]]


        # Connecting previous (ColumnNode's) with newly generated PreProcessorNodes ***
        if preprocessor.are_inputs_combined():
            # connect all input nodes with this node and vice versa:
            for prev_node in relevant_nodes:
                prev_node.append_node(pp_nodes[0])
        else:
            for (prev_node, this_node) in zip(relevant_nodes, pp_nodes):
                # connect every input node with its preprocessor node
                prev_node.append_node(this_node)


        # STATISTICS
        # collect statistics requirements:
        statistics_requirements = {pp_node.node_id : pp_node.define_statistics_requirements() for pp_node in pp_nodes}

        # if Statistics from DF are needed, a DF needs to be created based on the current status of the DAG
        def is_df_needed(statistics_requirements_):
            for node_id, dict_ in statistics_requirements_.items():
                for col_name, reqs in dict_.items():
                    if reqs != []:
                        return True

            return False

        def get_DF_dag():
            self._dag._create_query()
            objSqlTemplate = Template(self._dag.query)
            query_ = objSqlTemplate.safe_substitute(table_view=".".join([self.schema_name, self.table_name]))
            DF_dag = tdml.DataFrame.from_query(query_)
            return DF_dag

        DF_dag = None
        if is_df_needed(statistics_requirements):
            DF_dag = get_DF_dag()

        # collect statistics
        statistics_collected = collect_statistics_by_requirements(DF_dag, statistics_requirements)

        # CREATE SUCCESSORS
        for pp_node in pp_nodes:

            pp_node.fitted_statistics = statistics_collected[pp_node.node_id]
            pp_node.generate_and_append_successor_column_nodes()





    def fit(self, DF: tdml.DataFrame = None, schema_name: str = None, table_name: str = None):
        """
        Fits the pipeline to the given data step by step.

        Parameters
        ----------
        DF : tdml.DataFrame, optional
            The input DataFrame. If not provided, the DataFrame is loaded from the specified schema and table.
        schema_name : str, optional
            The name of the schema where the table is located. Required if DF is None.
        table_name : str, optional
            The name of the table to load. Required if DF is None.

        """
        assert tdml.get_context() is not None
        assert not ((DF is None) and ((schema_name is None) or (table_name is None)))

        if (DF is None):
            DF = tdml.DataFrame(tdml.in_schema(schema_name, table_name))
        else:
            # get table & schema name from DF
            DF._DataFrame__execute_node_and_set_table_name(DF._nodeid, DF._metaexpr)
            db_name = DF._table_name
            assert "." in db_name, "DataFrame must be created with explicit schema using tdml.in_schema(...)"
            # remove leading and trailing `"` to allow concatenation
            schema_name, table_name = [vn.replace('"', '') for vn in db_name.split(".")]

        self.schema_name = schema_name
        self.table_name = table_name
        self.DF = DF

        ### get Input Nodes for all columns
        cols_and_tdtypes = DF.tdtypes._column_names_and_types
        root_nodes = [ColumnNode(column_name,tdtype, "input") for (column_name, tdtype) in cols_and_tdtypes]
        for n in root_nodes:
            n.set_column_definition(n.column_name)

        ## grow DAG
        self._dag = DAG(root_nodes)
        print(f"{bcolors.Bold}Fitting started.{bcolors.ResetAll}")
        print(f"--------------------------------")
        for step_no, step in enumerate(self.steps):
            self._add_step_to_dag(step, step_no)
            print(f"{bcolors.Bold}Step {step_no+1} / {len(self.steps)} completed: {bcolors.ResetAll}{str(step[1])} on"
                  + f" {bcolors.LightGray}{str(step[0])}{bcolors.ResetAll}")


        self._is_fitted = True
        self._fit_df = DF
        print(f"--------------------------------")
        print(f"{bcolors.Bold}Fitting completed.{bcolors.ResetAll}")


    def get_output_column_names(self):
        """
        Returns the column names of the output columns of the fitted pipeline.

        Returns:
            output_column_names (list of str): The column names of the output columns of the fitted pipeline.

        Raises:
            AssertionError: If the pipeline is not fitted yet.
        """
        assert self._is_fitted
        return [node.column_name for node in self._dag.get_leaf_nodes()]

    # def transform_scored_dataset(self):
    #     # TODO: generate DAG based on output columns (leaves) from orig DAG
    #     # geht nur mit single input single output functions, like LabelEncoder, Scale, ...
    #
    #     pass

    def transform(self,
                  DF=None,
                  schema_name=None, table_name=None,
                  return_type="df",
                  create_replace_view=False,
                  output_schema_name=None,
                  output_view_name=None):
        """
        Apply the transformations in the pipeline to the input data.

        Parameters
        ----------
        DF : tdml.DataFrame, optional
            Input data in tdml.DataFrame format. If not provided, it will be fetched
            from the specified `schema_name` and `table_name`.
        schema_name : str, optional
            Schema name of the input data. Required if `DF` is not provided.
        table_name : str, optional
            Table name of the input data. Required if `DF` is not provided.
        return_type : {'df', 'str', None}, default='df'
            Specifies the return type of the transformed data:
                - 'df': returns a tdml.DataFrame
                - 'str': returns a SQL query string
                - None: returns nothing
        create_replace_view : bool, default=False
            Whether to create or replace a view with the transformed data in the database.
        output_schema_name : str, optional
            Schema name of the output view. Required if `create_replace_view` is True.
        output_view_name : str, optional
            Name of the output view. Required if `create_replace_view` is True.

        Returns
        -------
        tdml.DataFrame or str or None
            Transformed data as a tdml.DataFrame if `return_type` is 'df', SQL query string if
            `return_type` is 'str', or None if `return_type` is None.
        """

        assert self._is_fitted

        DbCon = tdml.get_context()
        assert DbCon is not None

        # argument checking
        if DF is not None:
            assert isinstance(DF, tdml.DataFrame)
            DF._DataFrame__execute_node_and_set_table_name(DF._nodeid, DF._metaexpr)
            view_name = DF._table_name
            # remove leading and trailing `"` to allow concatenation
            schema_name, table_name = [vn.replace('"', '') for vn in view_name.split(".")]
        else:
            assert isinstance(schema_name, str) and isinstance(table_name, str)
            DF = tdml.DataFrame(tdml.in_schema(schema_name,table_name))

        assert return_type in ["df", "str", None]

        if create_replace_view is True:
            assert isinstance(output_schema_name, str) and isinstance(output_view_name, str)

        ### get variation of dag:
        #columns not in DAG are just forwarded
        #column in DAG, not in DF are skipped.

        cols_and_tdtypes = DF.tdtypes._column_names_and_types
        dag_root_nodes = self._dag.root_nodes
        root_nodes_in_new_DF  = [node for node in dag_root_nodes if (node.column_name, node.tdtype) in cols_and_tdtypes]

        existing_column_dtypes = [(node.column_name, node.tdtype) for node in dag_root_nodes]

        additional_column_dtypes = [column_dtype for column_dtype in cols_and_tdtypes if column_dtype not in existing_column_dtypes]
        additional_nodes = [ColumnNode(column_name,tdtype, "input") for (column_name, tdtype) in additional_column_dtypes]
        for n in additional_nodes:
            n.set_column_definition(n.column_name)
        all_nodes = root_nodes_in_new_DF + additional_nodes

        transf_dag = DAG(all_nodes)
        transf_dag._create_query()

        transform_query = transf_dag.query
        objSqlTemplate = Template(transform_query)
        query = objSqlTemplate.safe_substitute(table_view = ".".join([schema_name, table_name]))

        if create_replace_view is True:
            objSqlTemplate = get_template("replaceview")
            pdicMapping = {
                "output_schema_name": output_schema_name,
                "output_view_name": output_view_name,
                "select_query": query
            }
            final_sql = objSqlTemplate.substitute(pdicMapping)
            execute_query(final_sql)
            print(f"VIEW {output_schema_name}.{output_view_name} created.")


        if return_type == "str":
            return query
        elif return_type == "df":
            if create_replace_view is True:
                DF_ret = tdml.DataFrame(tdml.in_schema(output_schema_name, output_view_name))
            else:
                DF_ret = tdml.DataFrame.from_query(query)
            return DF_ret
        else:  # also in case of None
            return



    def plot_sankey(self):
        """
        Plot the DAG (directed acyclic graph) of the pipeline using Sankey diagram.

        Returns
        -------
        plot : plotly.graph_objs._figure.Figure object
            Sankey plot of the DAG pipeline.
        """
        assert self._is_fitted

        return plot_dag_pipeline(self._dag)

    def to_dict(self):
        """
        Serialize a fitted Pipeline to a Python dictionary.

        This method asserts that the Pipeline instance is already fitted. The resulting
        dictionary can be used to reconstruct the Pipeline object with the `from_dict` class method.

        Returns
        -------
        dict
            A dictionary representation of the fitted Pipeline, suitable for serialization.

        Raises
        ------
        AssertionError
            If the Pipeline instance is not fitted.
        """
        assert self._is_fitted, "Pipeline must be fitted before serialization."
        return _serialize(self)

    def to_json(self, filepath: str):
        """
        Serialize the fitted Pipeline to a JSON file.

        This method serializes the Pipeline into a dictionary and then saves it as a JSON file
        at the specified filepath. The Pipeline must be fitted before calling this method.

        Parameters
        ----------
        filepath : str
            The path, including the filename, where the serialized Pipeline should be stored.
        """
        serialized_dict = self.to_dict()
        with open(filepath, 'w') as f:
            json.dump(serialized_dict, f, indent=4)


    @classmethod
    def from_dict(cls, pipeline_serialized_dict: dict):
        """
        Constructs a Pipeline object from a serialized dictionary.

        This class method deserializes a dictionary into a new Pipeline instance, initializing
        its properties and state based on the serialized data.

        Parameters
        ----------
        pipeline_serialized_dict : dict
            A dictionary containing serialized Pipeline data.

        Returns
        -------
        Pipeline
            A new Pipeline instance initialized with the data from the serialized dictionary.
        """
        new_DAG, pipeline_serialized, new_steps = _read_from_serialized(pipeline_serialized_dict)

        new_pipeline = cls(new_steps)

        new_pipeline._is_fitted = pipeline_serialized.get("_is_fitted", False)
        new_pipeline._needs_DF_for_fitting = pipeline_serialized.get("_needs_DF_for_fitting", False)
        new_pipeline._dag = new_DAG
        new_pipeline._fit_df = None
        new_pipeline._query = None

        return new_pipeline

    @classmethod
    def from_json(cls, filepath: str):
        """
        Constructs a Pipeline object from a JSON file.

        This class method reads a JSON file specified by `filepath`, deserializes it into a
        dictionary, and then uses that dictionary to construct a new Pipeline instance using
        the `from_dict` method.

        Parameters
        ----------
        filepath : str
            The path to the JSON file containing serialized Pipeline data.

        Returns
        -------
        Pipeline
            A new Pipeline instance initialized with the data from the JSON file.
        """
        with open(filepath, 'r') as f:
            pipeline_serialized_dict = json.load(f)
        return cls.from_dict(pipeline_serialized_dict)



    @classmethod
    def from_DataFrame(cls, DF: tdml.DataFrame, input_schema="", input_table="",  non_feature_cols=[], fit_pipeline=False):
        """
        Constructs a new Pipeline object from a teradataml DataFrame or view/table.

        You can either set the tdml.DataFrame parameter or specify input_schema and input_table names.

        This class method creates a new Pipeline instance based on the data and structure of the provided DataFrame.
        It generates a series of processing steps tailored to the data's characteristics and specified parameters,
        which are then used to instantiate the Pipeline. Optionally, it can also directly fit the constructed pipeline
        to the DataFrame if `fit_pipeline` is set to True.

        Parameters
        ----------
        DF : tdml.DataFrame
            The DataFrame from which to construct the pipeline. The data in this DataFrame is used to determine
            the processing steps in the pipeline.
        input_schema : str, optional
            A string representing the schema of the input data. This can be used to define or restrict the processing
            steps based on the schema information.
        input_table : str, optional
            A string representing the table name in the database from which the DataFrame is derived. This can be used
            for referencing in the pipeline's context.
        non_feature_cols : list, optional
            A list of column names to be excluded from feature processing. These columns will not be considered
            in the automatic step generation process. Use this for primary keys and target variables
        fit_pipeline : bool, optional
            If True, the constructed pipeline will be fitted to the provided DataFrame before it is returned.

        Returns
        -------
        Pipeline
            A new Pipeline instance, optionally fitted to the DataFrame.
        """
        steps = _get_auto_steps(DF, input_schema, input_table, non_feature_cols)

        new_pipeline = cls(steps)

        if fit_pipeline:
            new_pipeline.fit(DF)

        return new_pipeline


