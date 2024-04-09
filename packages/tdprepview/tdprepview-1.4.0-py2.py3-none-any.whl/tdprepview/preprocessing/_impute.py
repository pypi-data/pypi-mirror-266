from ._preprocessing import Preprocessor
from ._utils import (
    _is_valid_str_percentile)
from ..sql.generator import singlecol, multicol

class Impute(Preprocessor):
    """
    Imputes missing values in numerical columns using different strategies.

    Parameters
    ----------
    kind : str, optional
        The imputation strategy to use. The following values are possible:

        - 'mean': Replace missing values using the mean of the column.
        - 'mode': Replace missing values using the mode of the column.
        - 'min': Replace missing values using the minimum value of the column.
        - 'max': Replace missing values using the maximum value of the column.
        - 'median': Replace missing values using the median of the column.
        - 'custom': Replace missing values using a custom value or percentile.

        The default value is 'mean'.

    value : int, float, str, optional
        The value to use for the 'custom' imputation strategy. If the 'kind' parameter
        is not 'custom', this value is ignored. If 'value' is a string, it must be a
        percentile string of the form 'P[0-100]'. If 'value' is a number, it will be used
        as the constant value for imputation. The default value is 0.

    """

    def __init__(self, kind="mean", value=0):
        assert kind in ["mean","mode","min","max","median","custom"]
        if kind == "custom":
            assert (isinstance(value,(int,float) )
                    or (isinstance(value,str) & _is_valid_str_percentile(value)))
        self.kind = kind
        self.value = value
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return f"Impute"

    def define_necessary_statistics(self):
        if self.kind in ["mean","mode","min","max"]:
            return [("standard",)]
        elif self.kind in ["median"]:
            return [("median",)]
        elif self.kind in ["custom"]:
            if isinstance(self.value,str):
                return [("P", int(self.value[1:]))]
            else:
                return []
        else:
            return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:
        # 1. read relevant values from statistics
        new_vals = []
        for prev_col_name_internal, prev_col_name in zip(prev_col_names_internal,prev_col_names):
            if self.kind in ["mean", "mode", "min", "max", "median"]:
                new_vals.append(fitted_statistics[prev_col_name][self.kind])
            elif self.kind in ["custom"]:
                if isinstance(self.value,str):
                    # Percentile
                    new_vals.append(fitted_statistics[prev_col_name][str(self.value)])
                else:
                    # constant number
                    new_vals.append(self.value)

        # 2. call sql generate function
        sql_list = [singlecol.impute_num(prev_col_name_internal, new_val=new_val)  for
                    (prev_col_name_internal, new_val) in zip(prev_col_names_internal, new_vals) ]

        return sql_list


    def get_output_tdtype(self, input_tdtype = None) -> str:
        if input_tdtype in ["INTEGER()","FLOAT()","SMALLINT()","BIGINT()"]:
            return input_tdtype
        else:
            return ""

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return input_tdtypes


class SimpleImputer(Preprocessor):
    """
    Impute missing values using a specified strategy.

    Parameters
    ----------
    strategy : str, optional
        The imputation strategy to use. Options are "mean", "median", "most_frequent", and "constant".
        Default is "mean".
    fill_value : int or float, optional
        The value to use for missing values when strategy is "constant". Ignored for other strategies.
        Default is None.

    Returns
    -------
    Impute
        An Impute object that performs the specified imputation.

    Raises
    ------
    AssertionError
        If strategy is not one of "mean", "median", "most_frequent", or "constant".
        If strategy is "constant" and fill_value is not an int or float.

    Notes
    -----
    This class is based on the SimpleImputer class from scikit-learn's preprocessing module.

    """
    def __new__(cls, *, strategy='mean', fill_value=None):
        # arguments as per sklearn.preprocessing.SimpleImputer
        assert strategy in ["mean","median", "most_frequent", "constant"]
        if strategy == "constant":
            assert isinstance(fill_value, (int,float))

        translation = {
            "mean":"mean", "median":"median", "most_frequent":"mode", "constant":"custom"
        }

        return Impute(kind=translation[strategy], value=fill_value)


class ImputeText(Preprocessor):
    """
    Imputes missing values in text columns using different strategies.

    Parameters
    ----------
    kind : str, optional
        The type of imputation to perform, default is "mode". "mode" takes the most-frequent not-Null value.
        Valid options are "mode" and "custom".
    value : str, optional
        The custom value to use for imputation if kind is set to "custom".

    Raises
    ------
    AssertionError
        If kind is not one of the allowed values, or if the value parameter is not valid.

    Notes
    -----
    This class inherits from the Preprocessor abstract class and implements its abstract methods.
    """

    def __init__(self, kind="mode", value=""):
        assert kind in ["mode", "custom"]
        if kind == "custom":
            assert (isinstance(value,str))
        self.kind = kind
        self.value = value
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "ImputeText"

    def define_necessary_statistics(self):
        if self.kind in ["mode"]:
            return [("TOP",1)]
        elif self.kind in ["custom"]:
            return []
        else:
            return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:
        # 1. read relevant values from statistics
        new_vals = []
        if self.kind in ["custom"]:
            new_vals = [self.value for _ in prev_col_names]
        else:
            new_vals = [fitted_statistics[col]["top"][0] for col in prev_col_names]

        # 2. call sql generate function
        sql_list = [singlecol.impute_str(prev_col_name_internal, new_val=new_val)  for
                    (prev_col_name_internal, new_val) in zip(prev_col_names_internal, new_vals) ]
        return sql_list

    def get_output_tdtype(self, input_tdtype = None) -> str:
        return "VARCHAR()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return input_tdtypes


class IterativeImputer(Preprocessor):
    """
    Impute missing values using an iterative approach.

    Parameters
    ----------
    None

    Notes
    -----
    This class is based on the IterativeImputer class from scikit-learn's impute module.

    """

    def __init__(self):
        self.random_state = 42
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return f"IterativeImputer"

    def define_necessary_statistics(self):
        return [ ("IterativeImpute",)]

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:
        # 1. read relevant values from statistics


        means = {col:fitted_statistics[col]["mean"] for col in prev_col_names}
        intercepts = {col:fitted_statistics[col]["intercept"] for col in prev_col_names}
        regression_weights = {col:fitted_statistics[col]["regression_weights"] for col in prev_col_names}

        # 2. call sql generate function
        sql_list = multicol.iterative_imputer(prev_col_names_internal, prev_col_names, means,
                      intercepts, regression_weights)

        return sql_list

    def needs_subquery(self):
        return True

    def are_inputs_combined(self):
        return True

    def get_output_tdtype(self, input_tdtype = None) -> str:
        return "FLOAT()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return ["FLOAT()" for _ in input_tdtypes]
