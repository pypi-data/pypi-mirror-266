from ._preprocessing import Preprocessor
from ._utils import (
    _is_valid_str_percentile)
from ..sql.generator import singlecol, multicol


class Scale(Preprocessor):
    """
    Scales numerical values using a chosen method (MinMax, Z-Score, RobustScaling) and parameters.

    Parameters
    ----------
    kind : str
        The scaling method to use. Supported values are "minmax", "zscore", "robust", "maxabs" and "custom".
        Formulas:

        - 'minmax': (X - MIN(X)) / (MAX(X) - MIN(X)).
        - 'zscore': (X - MEAN(X)) / STD(X).
        - 'robust': (X - MEDIAN(X)) / (P75(X) - P25(X)).
        - 'maxabs': X / MAX(ABS(X))
        - 'custom': (X - numerator_subtr) / denominator.

    numerator_subtr : int or float or str
        The value to subtract from each element of the data before scaling. If a string, it must be one of
        "mean", "std", "median", "mode", "max", "min", or a string formatted as "P[0-100]" for percentiles.

    denominator : int or float or str
        The value to divide each element of the data by after subtracting numerator_subtr. If a string, it must
        be a formula composed of one or two of the following: "mean", "std", "median", "mode", "max", "min",
        or a string formatted as "P[0-100]" for percentiles (e.g. "MAX-P33"). If it's a single value, it must not be 0.

    zerofinull: bool, default True
        If the output should be 0 if the division would return null

    Raises
    ------
    AssertionError
        If any of the input values is invalid.

    Notes
    -----
    This class inherits from the Preprocessor abstract class and implements its abstract methods.
    """

    def __init__(self, kind="minmax", numerator_subtr=0, denominator=1, zerofinull=True,
                 feature_range=(0, 1), clip=False):
        assert kind in ["minmax", "zscore", "robust", "custom", "maxabs"]
        if kind == "minmax":
            assert (isinstance(feature_range, tuple)
                    and (len(feature_range) == 2)
                    and all([isinstance(x, (int, float)) for x in feature_range])
                    and (feature_range[0] < feature_range[1]))
            assert clip in [True, False]
        if kind == "custom":
            assert (isinstance(denominator, (int, float, str)))
            if isinstance(denominator, (int, float)):
                assert (denominator != 0)
            elif isinstance(denominator, str):
                denom_formula_comp = denominator.split("-")
                assert ((len(denom_formula_comp) in [1, 2]) and
                        (all([(c in ["mean", "std", "median", "mode", "max", "min"]) or _is_valid_str_percentile(c)
                              for c
                              in denom_formula_comp])))

            assert (isinstance(numerator_subtr, (int, float, str)))
            if isinstance(numerator_subtr, str):
                assert (numerator_subtr in ["mean", "std", "median", "mode", "max", "min"]) or _is_valid_str_percentile(
                    numerator_subtr)

        self.kind = kind
        self.numerator_subtr = numerator_subtr
        self.denominator = denominator
        self.zerofinull = zerofinull
        self.feature_range = feature_range
        self.clip = clip
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "Scale"

    def define_necessary_statistics(self):
        if self.kind in ["minmax", "zscore", "maxabs"]:
            return [("standard",)]
        elif self.kind in ["robust"]:
            return [("median",), ("P", 25), ("P", 75)]
        elif self.kind in ["custom"]:
            stats = [("standard",)]
            if isinstance(self.numerator_subtr, str):
                if _is_valid_str_percentile(self.numerator_subtr):
                    stats += [("P", int(self.numerator_subtr[1:]))]
                elif self.numerator_subtr in ["median"]:
                    stats += [("median",)]
                elif self.numerator_subtr in ["mean", "std", "mode", "max", "min"]:
                    stats += [("standard",)]
            if isinstance(self.denominator, str):
                denom_formula_comp = self.denominator.split("-")
                for comp in denom_formula_comp:
                    if _is_valid_str_percentile(comp):
                        stats += [("P", int(comp[1:]))]
                    elif comp in ["median"]:
                        stats += [("median",)]
                    elif self.numerator_subtr in ["mean", "std", "mode", "max", "min"]:
                        stats += [("standard",)]
            stats = list(set(stats))
            return stats
        else:
            return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:

        numerator_subtr_vals = []
        denominator_vals = []
        for prev_col_name_internal, prev_col_name in zip(prev_col_names_internal, prev_col_names):
            numerator_subtr, denominator = None, None
            if self.kind in ["minmax"]:
                numerator_subtr = fitted_statistics[prev_col_name]["min"]
                denominator = fitted_statistics[prev_col_name]["max"] - numerator_subtr
            elif self.kind in ["zscore"]:
                numerator_subtr = fitted_statistics[prev_col_name]["mean"]
                denominator = fitted_statistics[prev_col_name]["std"]
            elif self.kind in ["robust"]:
                numerator_subtr = fitted_statistics[prev_col_name]["median"]
                denominator = (fitted_statistics[prev_col_name]["P75"]
                               - fitted_statistics[prev_col_name]["P25"])

            elif self.kind in ["maxabs"]:
                numerator_subtr = 0
                min_val = fitted_statistics[prev_col_name]["min"]
                max_val = fitted_statistics[prev_col_name]["max"]
                max_abs = max(abs(min_val), abs(max_val))
                denominator = max_abs
            elif self.kind in ["custom"]:
                if isinstance(self.numerator_subtr, str):
                    if _is_valid_str_percentile(self.numerator_subtr):
                        numerator_subtr = fitted_statistics[prev_col_name]["P" + self.numerator_subtr[1:]]
                    elif self.numerator_subtr in ["median", "mean", "std", "mode", "max", "min"]:
                        numerator_subtr = fitted_statistics[prev_col_name][self.numerator_subtr]
                else:
                    numerator_subtr = self.numerator_subtr

                if isinstance(self.denominator, str):
                    denom_formula_comp = self.denominator.split("-")
                    comp_values = []
                    for comp in denom_formula_comp:
                        if comp in ["median", "mean", "std", "mode", "max", "min"]:
                            comp_values += [fitted_statistics[prev_col_name][comp]]
                        elif _is_valid_str_percentile(comp):
                            comp_values += [fitted_statistics[prev_col_name]["P" + comp[1:]]]
                    if len(comp_values) == 2:
                        denominator = comp_values[1] - comp_values[0]
                    else:
                        denominator = comp_values[0]
                else:
                    denominator = self.denominator

            numerator_subtr_vals += [numerator_subtr]
            denominator_vals += [denominator]

        # 2. call sql generate function
        if self.kind == "minmax" and ((self.feature_range != (0, 1)) or (self.clip == True)):
            # special cases, added for sklearn compatibility
            sql_list = [singlecol.scaleminmax(prev_col_name_internal, numerator_subtr, denominator, self.zerofinull,
                                              self.feature_range, self.clip)
                        for (prev_col_name_internal, numerator_subtr, denominator) in
                        zip(prev_col_names_internal, numerator_subtr_vals, denominator_vals)]
        else:
            sql_list = [singlecol.scale(prev_col_name_internal, numerator_subtr, denominator, self.zerofinull) for
                        (prev_col_name_internal, numerator_subtr, denominator) in
                        zip(prev_col_names_internal, numerator_subtr_vals, denominator_vals)]

        return sql_list

    def get_output_tdtype(self, input_tdtype=None) -> str:
        return "FLOAT()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return ["FLOAT()" for _ in input_tdtypes]


class StandardScaler:
    """
    Standardize features by removing the mean and scaling to unit variance.

    Parameters
    ----------
    with_mean : bool, default=True
        If True, center the data before scaling.
    with_std : bool, default=True
        If True, scale the data to unit variance.

    Returns
    -------
    scaler : Scale
        Returns an instance of Scale object that performs the transformation.

    """
    def __new__(cls, *, with_mean=True, with_std=True):
        # arguments as per sklearn.preprocessing.StandardScaler
        if (with_mean is True) and (with_std is True):
            return Scale(kind="zscore")
        else:
            numerator_subtr = 0
            denominator = 1
            if with_mean:
                numerator_subtr = 'mean'
            if with_std:
                denominator = 'std'
            return Scale(kind="custom", numerator_subtr=numerator_subtr, denominator=denominator, zerofinull=False)


class MaxAbsScaler:
    """
    Scale each feature by its maximum absolute value.

    Parameters
    ----------
    None

    Notes
    -----
    This scaler is meant for data that is already centered at zero or sparse data.
       """

    def __new__(cls):
        # arguments as per sklearn.preprocessing.MaxAbsScaler
        # copy is ignored
        return Scale(kind="maxabs", zerofinull=False)


class MinMaxScaler:
    """
    preprocessing.MinMaxScaler([feature_range, ...])
	Transform features by scaling each feature to a given range.
    """

    def __new__(cls, feature_range=(0, 1), *, clip=False):
        # arguments as per sklearn.preprocessing.MaxAbsScaler
        # copy is ignored
        return Scale(kind="minmax", feature_range=feature_range, clip=clip, zerofinull=False)


class RobustScaler:
    """
    Scale features using statistics that are robust to outliers.

    Parameters
    ----------
    with_centering : bool, default=True
        Whether to center the data before scaling.
    with_scaling : bool, default=True
        Whether to scale the data to the quantile range.
    quantile_range : tuple of floats (q_min, q_max), default=(25.0, 75.0)
        The quantile range to use when scaling the data.
    copy : bool, default=True
        Whether to make a copy of the input data. is ignored.
    unit_variance : bool, default=False
        This parameter is ignored.

    Returns
    -------
    scaled : Scale object
        The Scale object that performs the specified scaling.

    Notes
    -----
    This scaler scales the data based on the interquartile range (IQR) of the
    data, which makes it robust to outliers. The scaling is done according to
    the following formula:

        X_scaled = (X - median) / (P_qmax - P_qmin)

    where X is the input data, median is the median of the data, and P_qmax
    and P_qmin are the q_max and q_min quantiles of the data, respectively.
    The values of q_max and q_min are specified by the quantile_range parameter.

    If with_centering is True, the data will be centered by subtracting the median
    from it. If with_scaling is True, the data will be scaled according to the formula
    shown above. If both parameters are True, both centering and scaling will be
    performed.
    """

    def __new__(cls, *, with_centering=True, with_scaling=True, quantile_range=(25.0, 75.0),
                copy=True, unit_variance=False):
        q_min, q_max = quantile_range
        assert 0 <= q_min <= q_max <= 100
        assert unit_variance == False

        # arguments as per sklearn.preprocessing.RobustScaler
        # unit_variance, copy is ignored
        if (with_centering is True) and (with_scaling is True) and (quantile_range == (25.0, 75.0)):
            return Scale(kind="robust")
        else:
            numerator_subtr = 0
            denominator = 1
            if with_centering:
                numerator_subtr = 'median'
            if with_scaling:
                denominator = f"P{int(q_max)}-P{int(q_min)}"
            return Scale(kind="custom", numerator_subtr=numerator_subtr, denominator=denominator, zerofinull=False)


class CutOff(Preprocessor):
    """
    Clips numeric values that fall outside a given range.

    Parameters
    ----------
    cutoff_min : int, float, str or None, optional
        The minimum value for the range. If None, no lower bound will be applied.
        If a string, it must be in the format 'P[0-100]' or one of the values 'mean',
        'mode', 'median' or 'min', representing a percentile or summary statistic.
    cutoff_max : int, float, str or None, optional
        The maximum value for the range. If None, no upper bound will be applied.
        If a string, it must be in the format 'P[0-100]' or one of the values 'mean',
        'mode', 'median' or 'max', representing a percentile or summary statistic.

    Raises
    ------
    AssertionError
        If both `cutoff_min` and `cutoff_max` are None, or if they are equal.
        If `cutoff_min` or `cutoff_max` is not None and is not a valid type or value.

    Notes
    -----
    Values falling outside the range will be replaced by the closest value within the range.
    If a percentile is used for `cutoff_min` or `cutoff_max`, the value will be determined
    based on the corresponding percentile in the data set.
    """

    def __init__(self, cutoff_min=None, cutoff_max=None):
        assert not ((cutoff_min is None) and (cutoff_max is None))
        assert cutoff_min != cutoff_max
        if cutoff_min is not None:
            assert (isinstance(cutoff_min, (int, float))
                    or (isinstance(cutoff_min, str) & (_is_valid_str_percentile(cutoff_min) or
                                                       (cutoff_min in ["mean", "mode", "median", "min"])
                                                       )))
        if cutoff_max is not None:
            assert (isinstance(cutoff_max, (int, float))
                    or (isinstance(cutoff_max, str) & (_is_valid_str_percentile(cutoff_max) or
                                                       (cutoff_max in ["mean", "mode", "median", "max"])
                                                       )))

        self.cutoff_min = cutoff_min
        self.cutoff_max = cutoff_max
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "CutOff"


    def define_necessary_statistics(self):

        def get_stats_cutoff(cutoff_val):
            stats_ = []
            if cutoff_val is None:
                return []
            elif isinstance(cutoff_val, (int, float)):
                stats_ += []
            elif cutoff_val in ["mean", "mode", "min", "max"]:
                stats_ += [("standard",)]
            elif cutoff_val in ["median"]:
                stats_ += [("median",)]
            elif _is_valid_str_percentile(cutoff_val):
                if isinstance(cutoff_val, str):
                    stats_ += [("P", int(cutoff_val[1:]))]
            return stats_

        stats = get_stats_cutoff(self.cutoff_min) + get_stats_cutoff(self.cutoff_max)

        return stats


    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:

        # 1. read relevant values from statistics
        def get_cutoff_val(cuttof_variable, column_name):
            if (cuttof_variable is None) or isinstance(cuttof_variable, (float, int)):
                return cuttof_variable
            elif cuttof_variable in ["mean", "mode", "min", "max", "median"]:
                return fitted_statistics[column_name][cuttof_variable]
            elif _is_valid_str_percentile(cuttof_variable):
                return fitted_statistics[column_name]["P" + cuttof_variable[1:]]

        cutoff_min_vals = [get_cutoff_val(self.cutoff_min, column_name) for column_name in prev_col_names]
        cutoff_max_vals = [get_cutoff_val(self.cutoff_max, column_name) for column_name in prev_col_names]

        # 2. call sql generate function
        sql_list = [singlecol.cutoff(previous_col_name, cutoff_min, cutoff_max) for
                    (previous_col_name, cutoff_min, cutoff_max) in
                    zip(prev_col_names_internal, cutoff_min_vals, cutoff_max_vals)]

        return sql_list

    def needs_subquery(self):
        return True

    def get_output_tdtype(self, input_tdtype=None) -> str:
        return "FLOAT()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return ["FLOAT()" for _ in input_tdtypes]





class CustomTransformer(Preprocessor):
    """
    A custom transformer that applies a custom SQL expression to a column.

    Parameters:
    -----------
        custom_str (str): A custom SQL expression that contains the string "%%COL%%"
            where the column name should be inserted.
            For example: " 2 * POWER(%%COL%%, 2) + 3 * %%COL%% "

    Raises:
    -------
        AssertionError: If `custom_str` is not a string or does not contain "%%COL%%".

    """

    def __init__(self, custom_str, output_column_type = "FLOAT()"):
        assert isinstance(custom_str, str)
        assert "%%COL%%" in custom_str

        self.custom_str = custom_str
        self.output_column_type = output_column_type
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "CustomTransformer"

    def define_necessary_statistics(self):
        return []


    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:
        sql_list = [singlecol.custom_transformation(prev_col_name_internal, self.custom_str)
                    for prev_col_name_internal
                    in prev_col_names_internal]

        return sql_list

    def needs_subquery(self):
        return True

    def get_output_tdtype(self, input_tdtype=None) -> str:
        return self.output_column_type

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return [self.output_column_type for _ in input_tdtypes]




class Normalizer(Preprocessor):
    """
    A preprocessor that normalizes the input data. similar to sklearn's Normalizer

    Parameters
    ----------
    norm : str, optional (default='l2')
        The normalization method to use. Possible values are 'max', 'l1', and 'l2'.
    """

    def __init__(self, norm='l2'):
        assert norm in ["max", "l1", "l2"]
        self.norm = norm
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return f"Normalizer"

    def define_necessary_statistics(self):
        return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:

        sql_list = multicol.normalize(prev_col_names_internal, prev_col_names, self.norm)
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



class PowerTransformer(Preprocessor):
    """
    As PowerTransformer from sklearn:

    Apply a power transform featurewise to make data more Gaussian-like.
    Power transforms are a family of parametric, monotonic transformations that are applied to make data more
    Gaussian-like. This is useful for modeling issues related to heteroscedasticity (non-constant variance), or other
    situations where normality is desired.

    Currently, PowerTransformer supports the Box-Cox transform and the Yeo-Johnson transform. The optimal parameter
    for stabilizing variance and minimizing skewness is estimated through maximum likelihood.

    Box-Cox requires input data to be strictly positive, while Yeo-Johnson supports both positive or negative data.

    Parameters
    ----------
    method : str
        {‘yeo-johnson’, ‘box-cox’}, default=’yeo-johnson’
        The power transform method. Available methods are:
        ‘yeo-johnson’ [1], works with positive and negative values
        ‘box-cox’ [2], only works with strictly positive values
        See: https://scikit-learn.org/stable/modules/preprocessing.html#mapping-to-a-gaussian-distribution
    standardize : bool, will be ignored
        default=False
        No standardisation will take place. If desired, append StandardScaler

    Raises
    ------
    AssertionError
        If  `method` not in {‘yeo-johnson’, ‘box-cox’}

    """

    def __init__(self, method='yeo-johnson', standardize=False):
        assert method in ["yeo-johnson","box-cox"]

        self.method = method

        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "PowerTransformer"


    def define_necessary_statistics(self):
        return [("POWER_TRANSFORMER", self.method)]


    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:

        # 1. read relevant values from statistics
        lambdas_ = [fitted_statistics[c]["lambda"] for c in prev_col_names]

        sql_list = []
        if self.method == "yeo-johnson":
            sql_list = [singlecol.power_transform_yeojohnson(previous_col_name, lambda_)
                        for (previous_col_name, lambda_)
                        in zip(prev_col_names_internal, lambdas_)]


        else: #"box-cox"
            sql_list = [singlecol.power_transform_boxcox(previous_col_name, lambda_)
                        for (previous_col_name, lambda_)
                        in zip(prev_col_names_internal, lambdas_)]

        return sql_list

    def needs_subquery(self):
        return True

    def get_output_tdtype(self, input_tdtype=None) -> str:
        return "FLOAT()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return ["FLOAT()" for _ in input_tdtypes]

