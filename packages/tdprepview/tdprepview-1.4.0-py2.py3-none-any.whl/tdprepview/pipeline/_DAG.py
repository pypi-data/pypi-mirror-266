#DAG Directed Acyclic Graph
import uuid
import re
from abc import abstractmethod

from ..sql import get_template

INTENDATION  = "    "

def _parse_input_columns(input_columns, current_leaf_nodes):
    current_leaf_nodes_names = [node.column_name for node in current_leaf_nodes]
    if isinstance(input_columns,str):
        assert input_columns in current_leaf_nodes_names
        idx = current_leaf_nodes_names.index(input_columns)
        return [current_leaf_nodes[idx]]
    elif isinstance(input_columns, list):
        assert all([isinstance(c,str) for c in input_columns])
        assert all([ c in current_leaf_nodes_names for c in input_columns])
        idx_s = [current_leaf_nodes_names.index(c) for c in input_columns]
        return [current_leaf_nodes[idx] for idx in idx_s]
    elif isinstance(input_columns, dict):
        assert all([(k in ["prefix", "suffix", "pattern", "dtype_include", "dtype_exclude", "columns_exclude" ])
                    for k in input_columns.keys()])
        relevant_nodes = current_leaf_nodes
        # filter one criterion after the other
        if "prefix" in input_columns.keys():
            prefix = input_columns["prefix"]
            relevant_nodes = [node for node in relevant_nodes if node.column_name.startswith(prefix)]
        if "suffix" in input_columns.keys():
            suffix = input_columns["suffix"]
            relevant_nodes = [node for node in relevant_nodes if node.column_name.endswith(suffix)]
        if "pattern" in input_columns.keys():
            pattern = input_columns["pattern"]
            pattern = re.compile(pattern)
            relevant_nodes = [node for node in relevant_nodes
                                if bool(re.match(pattern, node.column_name))]
        if "dtype_include" in input_columns.keys():
            dtype_include = input_columns["dtype_include"]
            relevant_nodes = [node for node in relevant_nodes
                                if (node.tdtype in dtype_include)]

        if "dtype_exclude" in input_columns.keys():
            dtype_exclude = input_columns["dtype_exclude"]
            relevant_nodes = [node for node in relevant_nodes
                                if (node.tdtype not in dtype_exclude)]
        if "columns_exclude" in input_columns.keys():
            columns_exclude = input_columns["columns_exclude"]
            relevant_nodes = [node for node in relevant_nodes
                                if (node.column_name not in columns_exclude)]

        return relevant_nodes
    else:
        raise ValueError





class DAG:
    def __init__(self, root_nodes = []):
        self.root_nodes  = root_nodes
        self.query = None

    def get_leaf_nodes(self):
        depth_first_order = self.traverse_depthfirst()
        return [node for node in depth_first_order if node.is_leaf()]

    def traverse_breathfirst(self):
        breath_first_order = []

        nodes_to_visit = []
        nodes_to_visit += self.root_nodes

        visited_nodes = set()  # Keep track of visited nodes

        while len(nodes_to_visit)>0:
            next_node = nodes_to_visit.pop(0)
            breath_first_order.append(next_node)
            visited_nodes.add(next_node)  # Mark node as visited
            if not next_node.is_leaf():
                succesor_nodes = next_node.successor_nodes
                # filter if already visited or in nodes_to_visit
                succesor_nodes = [node for node in succesor_nodes if
                                 (node not in visited_nodes) and (node not in nodes_to_visit)]
                nodes_to_visit += succesor_nodes

        return breath_first_order


    def traverse_depthfirst(self):
        depth_first_order = []

        def visit(node):
            depth_first_order.append(node)
            for succ in node.successor_nodes:
                if succ not in depth_first_order:
                    visit(succ)

        for node in self.root_nodes:
            visit(node)

        return depth_first_order

    def _create_query(self):
        breath_first_order = self.traverse_breathfirst()
        leaf_nodes = self.get_leaf_nodes()

        withas_select_clauses = ["".join(node.get_select_clause_part_withas()) for node in breath_first_order]
        leaves_select_clauses = ["".join(leaf.get_select_clause_part_leaf()) for leaf in leaf_nodes]

        def add_comma_if_necessary(withas_select_clause_):

            idx_last_column_clause = None
            for idx in list(range(len(withas_select_clause_)))[::-1]:
                if withas_select_clause_[idx].startswith("\n\n"):
                    continue
                else:
                    idx_last_column_clause = idx
                    break

            new_withas_select_clause_ = []

            for idx, clause in enumerate(withas_select_clause_):
                if clause.startswith("\n\n"):
                    new_withas_select_clause_.append(clause)
                elif clause == "":
                    new_withas_select_clause_.append(clause)
                elif idx == idx_last_column_clause:
                    new_withas_select_clause_.append(clause)
                else:
                    new_withas_select_clause_.append(clause+",")

            return new_withas_select_clause_

        withas_select_clauses = add_comma_if_necessary(withas_select_clauses)

        withas_select_clause = INTENDATION + f"\n{INTENDATION}".join(
            [x for x in withas_select_clauses if x!= ""])

        leaves_select_clause = INTENDATION + f",\n{INTENDATION}".join(
            [x for x in leaves_select_clauses if x != ""])

        template_withas = get_template("withas")
        template_from = get_template("from")

        # missing: final_query, must be replaced by later version
        part1_withas = template_withas.safe_substitute(intermediate_name="preprocessing_steps",
                                                       column_definitions=withas_select_clause
                                                       )

        part2_from = template_from.safe_substitute(column_definitions=leaves_select_clause,
                                                   table_view_query="preprocessing_steps")


        self.query = "\n\n".join([part1_withas, part2_from])


class Node:
    def __init__(self):
        self.node_id = str(uuid.uuid4()).replace("-","")
        self.prev_nodes  = []
        self.successor_nodes = []

        self.clauses_withas = []
        self.clauses_final = []

    def __hash__(self):
        return hash(self.node_id)

    def __eq__(self, other):
        return self.node_id == other.node_id

    @abstractmethod
    def is_leaf(self):
        pass

    def get_leaf_nodes(self):
        if self.is_leaf():
            return([self])
        else:
            dag_ = DAG(root_nodes=self.successor_nodes)
            return dag_.get_leaf_nodes()

    def append_node(self,successor_node):
        """
        `self` is the previous node, and successor_node is the node to be appended
        does a bidirectional appending, for easier browsing
        """
        self.successor_nodes.append(successor_node)
        successor_node.prev_nodes.append(self)

    @abstractmethod
    def get_select_clause_part_withas(self):
        pass

    @abstractmethod
    def get_select_clause_part_leaf(self):
        pass



class ColumnNode(Node):

    COUNTER_INTERNAL = 0

    def __init__(self, column_name, tdtype, preprocessor_name:str = "input"):
        super().__init__()
        self.column_name = column_name #clear name
        # CHANGE TO SHORTEN NAMES:
        #self.column_name_internal = self.column_name +"__"+ preprocessor_name +"_"+ self.node_id
        self.column_name_internal = "c_i_" + str(ColumnNode.COUNTER_INTERNAL)
        ColumnNode.COUNTER_INTERNAL += 1

        self.tdtype = tdtype
        self.column_definition = None

    def is_leaf(self):
        if (self.successor_nodes == []) or (self.successor_nodes is None):
            return True
        elif (len(self.successor_nodes) == 1) and (
                (self.successor_nodes[0].successor_nodes is None)
            or (self.successor_nodes[0].successor_nodes == [])):
            return True
        else:
            return False

    def set_column_definition(self, column_definition:str):
        self.column_definition = column_definition

    def get_select_clause_part_withas(self):
        assert self.column_definition is not None
        return [self.column_definition," AS ",self.column_name_internal]

    def get_select_clause_part_leaf(self):
        if self.is_leaf():
            return  [self.column_name_internal," AS ",self.column_name]
        else:
            return []




class PreProcesserNode(Node):
    def __init__(self, preprocessor, step_number, options, first_node_with_preprocessor = False):
        super().__init__()
        self.preprocessor = preprocessor
        self.options = options
        self.fitted_statistics = {}
        self.step_number = step_number
        self.comment = None
        if first_node_with_preprocessor:
            self.comment = f"-- Step {int(self.step_number)}: {self.preprocessor}"

    def is_leaf(self):
        return False


    def get_select_clause_part_withas(self):
        return ""
        # TODO: once fix travesing tree for comments to be at right position
        # if self.comment is not None:
        #     return [f"\n\n{INTENDATION}{self.comment}"]
        # else:
        #     return ""

    def get_select_clause_part_leaf(self):
        # PreProcesserNode will never be leave
        return []

    def define_statistics_requirements(self):

        stats_req = self.preprocessor.necessary_statistics # list of requirements
        if len(stats_req) ==0:
            return {}
        else:
            column_list = [prev_col_node.column_name for prev_col_node in self.prev_nodes]
            # eg {"columns":["f1","f2",...], "required_statistics":["median","standard"]}
            return {"columns": column_list, "required_statistics": stats_req}



    def generate_and_append_successor_column_nodes(self):

        prefix = self.options.get("prefix", "")
        suffix = self.options.get("suffix", "")


        if not self.preprocessor.are_output_columns_different():
            # exactly 1 input for every output
            if self.preprocessor.are_inputs_combined():
                suc_col_names_, output_tdtypes_, prev_col_names_internal_, prev_col_names = [],[],[],[]
                for prev_col_node in self.prev_nodes:
                    suc_col_names_.append(prefix + prev_col_node.column_name + suffix)
                    output_tdtypes_.append(self.preprocessor.get_output_tdtype(prev_col_node.tdtype))
                    prev_col_names_internal_.append(prev_col_node.column_name_internal)
                    prev_col_names.append(prev_col_node.column_name)

                suc_column_definitions_ = self.preprocessor.generate_sql_columns(
                    prev_col_names_internal_, prev_col_names, self.fitted_statistics)

                for suc_col_name, output_tdtype, suc_column_definition in \
                        zip(suc_col_names_, output_tdtypes_, suc_column_definitions_):
                    suc_col_node = ColumnNode(suc_col_name, output_tdtype, str(self.preprocessor))
                    suc_col_node.set_column_definition(suc_column_definition)

                    self.append_node(suc_col_node)

            else:
                for prev_col_node in self.prev_nodes:

                    suc_col_name = prefix + prev_col_node.column_name + suffix

                    output_tdtype = self.preprocessor.get_output_tdtype(prev_col_node.tdtype)

                    prev_col_name_internal = prev_col_node.column_name_internal
                    prev_col_name = prev_col_node.column_name

                    suc_column_definition = self.preprocessor.generate_sql_columns(
                        [prev_col_name_internal], [prev_col_name], self.fitted_statistics )[0]

                    suc_col_node = ColumnNode(suc_col_name, output_tdtype, str(self.preprocessor))
                    suc_col_node.set_column_definition(suc_column_definition)

                    self.append_node(suc_col_node)

        else:
            new_column_nodes = []
            # output does not depend on previous columns, but on the fitted statistics and the Preprocessor function
            prev_col_names_internal = [prev_col_node.column_name_internal  for prev_col_node in self.prev_nodes]
            prev_col_names = [prev_col_node.column_name for prev_col_node in self.prev_nodes]
            prev_col_tdtypes = [prev_col_node.tdtype for prev_col_node in self.prev_nodes]

            suc_column_definitions = self.preprocessor.generate_sql_columns(
                prev_col_names_internal, prev_col_names, self.fitted_statistics)

            suc_column_names = [prefix+colname+suffix for colname
                                  in self.preprocessor.generate_column_output_names(self.fitted_statistics)]

            suc_output_tdtypes = self.preprocessor.generate_column_output_tdtypes(
                prev_col_tdtypes, self.fitted_statistics)

            for suc_col_name, suc_column_definition, output_tdtype in zip(
                    suc_column_names, suc_column_definitions, suc_output_tdtypes):
                suc_col_node = ColumnNode(suc_col_name, output_tdtype, str(self.preprocessor))
                suc_col_node.set_column_definition(suc_column_definition)
                self.append_node(suc_col_node)









