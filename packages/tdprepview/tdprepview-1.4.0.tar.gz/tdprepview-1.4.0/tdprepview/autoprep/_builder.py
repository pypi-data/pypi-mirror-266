import teradataml as tdml
from ._checker import (_check_imputation,
        _check_minmaxscaling,
        _check_powertransformer,
        _check_textencoding)
from ..preprocessing import *

SAMPLE_SIZE = 50000

def _preprocess_pipeline(df, teradata_dtype_features, non_feature_cols, return_str=False):
    """
    Generates a preprocessing pipeline for a given dataframe based on the columns' data types.

    Parameters:
    df (DataFrame): The dataframe to preprocess.
    teradata_dtype_features (list of tuples): List containing column names and their Teradata data types.
    non_feature_cols (list): List of columns to exclude from feature preprocessing.

    Returns:
    list: A list of tuples, where each tuple contains the column(s) and their associated preprocessing step.
    """

    teradata_dtype_features = [(cn, dt) for (cn, dt) in teradata_dtype_features if cn not in non_feature_cols]

    def summarize_preprocess_steps(check_function):
        preprocess_steps = {}
        for column_name, data_type in teradata_dtype_features:
            prep = check_function(df, column_name, data_type)
            if prep:
                preprocess_steps[column_name] = prep

        summary = {}
        for key, value in preprocess_steps.items():
            val_str = str(value)
            summary.setdefault(val_str, []).append(key)

        return [(keys, eval(value_str)) for value_str, keys in summary.items()]

    # Compile all preprocessing steps
    all_steps = []
    preprocess_functions = [
        _check_imputation,
        _check_minmaxscaling,
        _check_powertransformer,
        _check_textencoding
    ]

    for func in preprocess_functions:
        all_steps.extend(summarize_preprocess_steps(func))

    # Include casting for non-feature columns
    all_steps.append(({"columns_exclude": non_feature_cols},
                      {'preprocessor': 'Cast', 'parameters': {'new_type': 'FLOAT'}}))

    # Print and construct the final steps

    final_steps_str = []
    final_steps = []
    for colexpr, prep_dict in all_steps:
        prep = prep_dict['preprocessor']
        params = prep_dict['parameters']
        preprocessor_instance = eval(f"{prep}(**{params})")
        final_steps.append((colexpr, preprocessor_instance))
        final_steps_str.append(f"     ({str(colexpr)}, \n\t\t\t\t tdprepview.{prep}(**{params}))")

    final_steps_str = "[\n" + ",\n\n".join(final_steps_str) + "\n]"
    if return_str:
        return final_steps_str
    else:
        return final_steps


def _get_auto_steps(DF, input_schema="", input_table="", non_feature_cols=[]):
    assert (DF is not None) or ((type(input_schema) == str) and (type(input_table) == str))
    if DF is None:
        DF = tdml.DataFrame(tdml.in_schema(input_schema, input_table))

    df = DF.sample(n=SAMPLE_SIZE, randomize=True).to_pandas(all_rows=True).reset_index()
    colname_dtypes = DF.tdtypes._column_names_and_types

    steps = _preprocess_pipeline(df, colname_dtypes, non_feature_cols, return_str=False)
    return steps


def auto_code(DF, input_schema="", input_table="", non_feature_cols=[]):
    """
      Generates a string containing tdprepview code for the steps of a suggested preprocessing pipeline based on the
      input DataFrame or database table schema.

      This function examines the data's characteristics or the database schema to automatically generate Python code that
      outlines the steps for preprocessing the data. The generated code can be used as a starting point for data
      preprocessing tasks in a ClearScape machine learning workflow.

      Parameters
      ----------
      DF : tdml.DataFrame or None
          A teradataml DataFrame whose data is used to determine preprocessing steps. If None, `input_schema` and
          `input_table` must be provided to generate the DataFrame from the database schema.
      input_schema : str, optional
          A string representing the schema of the input data in the database. This is used in conjunction with
          `input_table` to generate the DataFrame if `DF` is None.
      input_table : str, optional
          A string representing the table/view name in the database from which to generate the DataFrame if `DF` is None.
      non_feature_cols : list, optional
          A list of column names to be excluded from the preprocessing steps. These columns will not be considered in the
          generated code, typically used for columns like IDs or target variables.

      Returns
      -------
      str
          A string containing the Python code for the suggested preprocessing pipeline.
      """
    assert (DF is not None) or ((type(input_schema) == str) and (type(input_table) == str))
    if DF is None:
        DF = tdml.DataFrame(tdml.in_schema(input_schema, input_table))

    df = DF.sample(n=SAMPLE_SIZE, randomize=True).to_pandas(all_rows=True).reset_index()
    colname_dtypes = DF.tdtypes._column_names_and_types

    steps_str = _preprocess_pipeline(df, colname_dtypes, non_feature_cols, return_str=True)
    return steps_str