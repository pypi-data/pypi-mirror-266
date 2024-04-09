from ._preprocessing import Preprocessor
from ._utils import (
    _is_valid_str_percentile,
    _is_valid_str_top)
from ..sql.generator import singlecol

class FixedWidthBinning(Preprocessor):
    """
    Performs fixed-width binning on a numerical column.

    Parameters
    ----------
    n_bins: int
        The number of bins to divide the data into. Must be greater than 1. bins range from 0 to n_bins-1
    lower_bound: float or None, default=None
        The lower bound of the binning range. If None, the minimum value in the data is used.
    upper_bound: float or None, default=None
        The upper bound of the binning range. If None, the maximum value in the data is used.

    Raises
    ------
    AssertionError:
        If n_bins is not an integer or is not greater than 1.
        If lower_bound is not None or a float/int.
        If upper_bound is not None or a float/int.

    Notes
    -----
    This preprocessor creates bins of fixed width for numerical data. The data is divided into n_bins
    equally sized intervals in the range defined by lower_bound and upper_bound. If these values are not
    provided, the minimum and maximum values of the data are used as bounds.
    """

    def __init__(self, n_bins=5, lower_bound=None, upper_bound=None):
        assert isinstance(n_bins, int)
        assert n_bins > 1
        assert (lower_bound is None) or isinstance(lower_bound, (float,int))
        assert (upper_bound is None) or isinstance(upper_bound, (float, int))

        self.n_bins = n_bins
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "FixedWidthBinning"

    def define_necessary_statistics(self):
        if isinstance(self.lower_bound, (float,int)) & isinstance(self.upper_bound, (float,int)):
            return []
        else:
            return [("standard",)]

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:
        # 1. read relevant values from statistics
        c_min_vals = []
        c_max_vals = []

        for prev_col_name_internal, prev_col_name in zip(prev_col_names_internal, prev_col_names):
            if self.lower_bound is None:
                c_min = fitted_statistics[prev_col_name]["min"]
            else:
                c_min = self.lower_bound

            if self.upper_bound is None:
                c_max = fitted_statistics[prev_col_name]["max"]
            else:
                c_max = self.upper_bound

            c_min_vals += [c_min]
            c_max_vals += [c_max]

        # 2. call sql generate function
        sql_list = [singlecol.fixed_width_binning(prev_col_name_internal, self.n_bins, c_max, c_min) for
                    (prev_col_name_internal, c_max, c_min) in zip(prev_col_names_internal, c_min_vals, c_max_vals)]

        return sql_list

    def get_output_tdtype(self, input_tdtype=None) -> str:
        return "INTEGER()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return ["INTEGER()" for _ in input_tdtypes]


class VariableWidthBinning(Preprocessor):
    """
    Binning numerical data into variable-width bins.

    Binning can be performed in two ways:
        - 'quantiles': bin data into no_quantiles number of bins based on percentiles.
        - 'custom': bin data based on custom boundaries provided by the user.

    Parameters:
    -----------
    kind : str, default 'quantiles'
        Method of binning. Valid options: 'quantiles', 'custom'.
    no_quantiles : int, default 5
        Number of bins to use when kind='quantiles'.
        Valid values are between 2 and 100.
    boundaries : list of floats or ints, default None
        Boundaries to use when kind='custom'. Must be sorted in ascending order.

    Raises:
    -------
    ValueError:
        If kind is not 'quantiles' or 'custom', or if no_quantiles is not an integer
        between 2 and 100, or if boundaries is not a list of floats or ints sorted
        in ascending order.

    """
    def __init__(self, kind="quantiles", no_quantiles=5, boundaries=None):
        assert kind in ["quantiles","custom"]
        if kind == "quantiles":
            assert isinstance(no_quantiles,int)
            assert 2 <= no_quantiles <= 100
        if kind == "custom":
            assert isinstance(boundaries, list)
            assert all(isinstance(val, (int,float)) for val in boundaries)
            #check if list is sorted

            assert all(boundaries[i] < boundaries[i+1] for i in range(len(boundaries) - 1)), "boundaries list not sorted"

        self.kind = kind
        self.no_quantiles = no_quantiles
        self.boundaries = boundaries
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "VariableWidthBinning"

    def define_necessary_statistics(self):
        if self.kind in ["custom"]:
            return []
        elif self.kind in ["quantiles"]:
            step = 100.0/self.no_quantiles
            quantiles = [int(step*i) for i in range(1,self.no_quantiles)]
            return [("P", q) for q in quantiles]
        else:
            return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:

        bin_boundaries_vals = []

        for column_name in prev_col_names:
            bin_boundaries = []
            # 1. read relevant values from statistics
            if self.kind in ["custom"]:
                bin_boundaries = self.boundaries
            elif self.kind in ["quantiles"]:
                step = 100.0/self.no_quantiles
                quantiles = [int(step*i) for i in range(1,self.no_quantiles)]
                for qu in quantiles:
                    bin_boundaries.append(fitted_statistics[column_name]["P"+str(qu)])

            bin_boundaries_vals += [bin_boundaries]

        sql_list = [singlecol.variable_width_binning(prev_col_name_internal, bin_boundaries)
                    for (prev_col_name_internal, bin_boundaries)
                    in zip(prev_col_names_internal, bin_boundaries_vals)]

        return sql_list

    def needs_subquery(self):
        return True

    def get_output_tdtype(self, input_tdtype=None) -> str:
        return "INTEGER()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return ["INTEGER()" for _ in input_tdtypes]


class QuantileTransformer:
    """
    Transform features using quantiles information.

    Parameters
    ----------
    n_quantiles : int, optional
        Number of quantiles to compute. Default is 10.
    output_distribution : str, optional
        The output distribution. Only 'uniform' is currently supported. Default is 'uniform'.
    ignore_implicit_zeros : bool, optional
        Whether to ignore implicit zero values when computing the quantiles. Default is False.
    subsample : int or None, optional
        If not None, subsample the dataset to this size for computing the quantiles. Default is None. is ignored.
    random_state : int or None, optional
        Seed for the random number generator. Default is None. is ignored.
    copy : bool, optional
        Whether to copy the input array before transforming it. Default is True. is ignored.

    Returns
    -------
    QuantileTransformer
        A QuantileTransformer object that can be used to transform data using quantile information.

    Notes
    -----
    This class is based on the QuantileTransformer class from scikit-learn's preprocessing module.

    """
    def __new__(cls, * , n_quantiles=10, output_distribution='uniform', ignore_implicit_zeros=False,
                subsample=None, random_state=None, copy=True):
        # arguments as per sklearn.preprocessing.MaxAbsScaler
        # output_distribution, ignore_implicit_zeros, subsample, random_state, copy is ignored
        assert output_distribution == 'uniform'
        # normal distribution not supported
        # TODO: support normal distribution,  by including this: https://arxiv.org/pdf/2206.12601.pdf
        return VariableWidthBinning(kind="quantiles", no_quantiles=n_quantiles)


class DecisionTreeBinning(Preprocessor):
    """
    Binning numerical data into variable-width bins, based on a decision tree.
    Trees are trained in sklearn.

    Parameters:
    -----------
    target_var : str, default None
        Variable to use as target variable
    model_type: str, default "classification"
        Either "classification" or "regression"
    no_bins : int, default 10
        Number of bins (= number of leaves in decision tree).
        Valid values are between 2 and 100.
    no_rows : int, default 10000
        Number of rows that are randomly sampled and used for fitting the tree.
        Must be between 100 than 100000

    Raises:
    -------
    AssertionError: If `target_var` is None, ...

    """
    def __init__(self, target_var=None, model_type="classification", no_bins=10):
        assert target_var is not None
        assert model_type in ["classification","regression"]
        assert isinstance(no_bins,int) and (2 <= no_bins <= 100)

        self.target_var = target_var
        self.model_type = model_type
        self.no_bins = no_bins
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "DecisionTreeBinning"

    def define_necessary_statistics(self):
        return [("TREE", self.target_var, self.model_type, self.no_bins)]

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:

        bin_boundaries_vals = [fitted_statistics[col]["tree_bins"] for col in prev_col_names]

        sql_list = [singlecol.variable_width_binning(prev_col_name_internal, bin_boundaries)
                    for (prev_col_name_internal, bin_boundaries)
                    in zip(prev_col_names_internal, bin_boundaries_vals)]

        return sql_list

    def needs_subquery(self):
        return True

    def get_output_tdtype(self, input_tdtype=None) -> str:
        return "INTEGER()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return ["INTEGER()" for _ in input_tdtypes]


class ThresholdBinarizer(Preprocessor):
    """
    Binarizes numeric data using a threshold value.

    Parameters
    ----------
    threshold : int, float or str, optional
        The threshold used for binarization. If a string, it can be one of "mean", "mode", "median" or a percentile
        string in the format of "P[1-100]", e.g "P33". Default is "mean".

    Notes
    -----
    If a value is greater than the threshold, the output is 1, else 0.
    """
    def __init__(self, threshold="mean"):
        if isinstance(threshold,str):
            assert (threshold in ["mean","mode","median"]) or _is_valid_str_percentile(threshold)
        else:
            assert isinstance(threshold,(int,float))
        self.threshold = threshold
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "ThresholdBinarizer"

    def define_necessary_statistics(self):
        if isinstance(self.threshold,(int,float)):
            return []
        elif self.threshold in ["median"]:
            return [("median",)]
        elif self.threshold in ["mean", "mode"]:
            return [("standard",)]
        elif _is_valid_str_percentile(self.threshold):
            return [("P", int(self.threshold[1:]))]
        else:
            return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:
        # 1. read relevant values from statistics
        threshold_vals = []

        if isinstance(self.threshold,(int,float)):
            threshold_vals = [self.threshold for _ in prev_col_names]
        elif self.threshold in ["mean","mode","median"]:
            threshold_vals = [fitted_statistics[col][self.threshold] for col in prev_col_names]
        elif _is_valid_str_percentile(self.threshold):
            threshold_vals = [fitted_statistics[col]["P"+self.threshold[1:]] for col in prev_col_names]

        sql_list = [singlecol.threshold_binarizer(prev_col_name_internal, threshold)
                    for (prev_col_name_internal, threshold)
                    in zip(prev_col_names_internal, threshold_vals)]

        return sql_list

    def get_output_tdtype(self, input_tdtype=None) -> str:
        return "INTEGER()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return ["INTEGER()" for _ in input_tdtypes]


class Binarizer:
    """
    Binarize data according to a threshold.

    Parameters
    ----------
    threshold : float or int, optional
        The threshold value to use for binarization. Default is 0.0.
    copy : bool, optional
        Whether to copy the input array before binarizing it. Default is True. is ignored

    Notes
    -----
    This class is based on the Binarizer class from scikit-learn's preprocessing module.

    """
    def __new__(cls, *, threshold=0.0, copy=True):
        # arguments as per sklearn.preprocessing.Binarizer
        # copy is ignored
        assert isinstance(threshold,(float,int))
        return ThresholdBinarizer(threshold=threshold)


class ListBinarizer(Preprocessor):
    """
    Preprocessor for text columns that outputs 1 if the value is in a given list or among the K most frequent values.

    Parameters
    ----------
    elements1 : str or list of str
        The list of elements to binarize or the top K most frequent values, indicated by "TOPK", e.g. "TOP3" or "TOP10".

    """

    def __init__(self, elements1="TOP3"):
        if isinstance(elements1,list):
            assert(all([isinstance(c, str) for c in elements1]))
        else:
            assert _is_valid_str_top(elements1)

        self.elements1 = elements1
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "ListBinarizer"

    def define_necessary_statistics(self):
        if isinstance(self.elements1,list):
            return []
        elif _is_valid_str_top(self.elements1):
            return [("TOP", int(self.elements1[3:]))]
        else:
            return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:
        # 1. read relevant values from statistics
        if isinstance(self.elements1,list):
            classes_1_vals = [self.elements1 for _ in prev_col_names]
        else:
            classes_1_vals = [fitted_statistics[col]["top"] for col in prev_col_names]

        sql_list = [singlecol.list_binarizer(prev_col_name_internal, classes_1)
                    for (prev_col_name_internal, classes_1)
                    in zip(prev_col_names_internal, classes_1_vals)]

        return sql_list

    def get_output_tdtype(self, input_tdtype=None) -> str:
        return "INTEGER()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return ["INTEGER()" for _ in input_tdtypes]


class LabelEncoder(Preprocessor):
    """
    Encodes a text column into numerical values using a label encoding scheme.

    The encoding can be based on the K most frequent values, as defined by a TOPK value,
    or on a custom list of elements.

    Parameters:
    -----------
    elements: list or str
        If a list, contains the custom elements to use for encoding the column. If a string, should be a valid TOPK
        specifier, indicating that the K most frequent elements should be used. E.g. "TOP20"

    Raises:
    -------
    AssertionError:
        If the `elements` parameter is not a list or a valid TOPK specifier. If `elements` is a list, raises an
        AssertionError if it contains non-string elements.
    """

    #     # TODO: inverse_transform
    #TODO: make labelEncoder also work with non-varchar, e.g. by casting
    def __init__(self, elements="TOP100"):
        assert isinstance(elements, list) or isinstance(elements, str)
        if isinstance(elements, list):
            assert (all([isinstance(val, str) for val in elements]))
        if isinstance(elements, str):
            assert(_is_valid_str_top(elements))

        self.elements = elements
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "LabelEncoder"

    def define_necessary_statistics(self):
        if isinstance(self.elements, list):
            return []
        elif isinstance(self.elements, str):
            return [("TOP", int(self.elements[3:]))]
        else:
            return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:

        classes_vals = []

        for column_name in prev_col_names:
            classes = []
            # 1. read relevant values from statistics
            if isinstance(self.elements, list):
                classes = self.elements
            elif _is_valid_str_top(self.elements):
                classes = fitted_statistics[column_name]["top"]

            classes_vals += [classes]

        sql_list = [singlecol.label_encoder(prev_col_name_internal, classes)
                    for (prev_col_name_internal, classes)
                    in zip(prev_col_names_internal, classes_vals)]

        return sql_list

    def needs_subquery(self):
        return True

    def get_output_tdtype(self, input_tdtype=None) -> str:
        return "INTEGER()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        # important only for those functions where are_output_columns_different == True
        return ["INTEGER()" for _ in input_tdtypes]








