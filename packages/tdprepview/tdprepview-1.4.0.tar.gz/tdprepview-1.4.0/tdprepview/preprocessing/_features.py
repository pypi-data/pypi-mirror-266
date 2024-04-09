from ._preprocessing import Preprocessor
from ..sql.generator import multicol


class PolynomialFeatures(Preprocessor):
    """
    Generate polynomial and interaction features from input data.

    Parameters
    ----------
    degree : int, optional
        The degree of the polynomial features. Default is 2.
    interaction_only : bool, optional
        Whether to generate only interaction features (i.e., products of distinct features).
        Default is False.

    Notes
    -----
    This class is based on the PolynomialFeatures class from scikit-learn's preprocessing module.

    """

    def __init__(self, degree=2, interaction_only = False):
        assert isinstance(degree, int)
        self.degree = degree
        self.interaction_only = interaction_only

        self.necessary_statistics = self.define_necessary_statistics()

        self._output_col_formula = None
        self._output_col_name = None

    def __str__(self):
        return "PolynomialFeatures"

    def define_necessary_statistics(self):
        return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:

        if self._output_col_formula is None:
            sql_list_tuples = multicol.polynomial_features(prev_col_names_internal, prev_col_names, self.degree,
                                                           self.interaction_only)
            [output_col_formula, output_col_name ] = [list(t) for t in zip(*sql_list_tuples)]
            self._output_col_formula = output_col_formula
            self._output_col_name = output_col_name

        return self._output_col_formula

    def needs_subquery(self):
        return True

    def are_inputs_combined(self):
        return True

    def are_output_columns_different(self):
        return True

    def get_output_tdtype(self, input_tdtype = None) -> str:
        return "FLOAT()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        #generate_sql_columns must be called first
        assert self._output_col_name is not None
        return self._output_col_name

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return ["FLOAT()" for i in range(len(self._output_col_name))]


class OneHotEncoder(Preprocessor):
    """
    One-hot encoder for categorical features.

    Parameters
    ----------
    categories : 'auto' or list, default='auto'
        Categories to encode. 'auto' means that categories will be inferred from
        the training data. A list of categories can also be provided.
    handle_unknown : {'ignore'}, default='ignore'
        Whether to ignore unknown categories during transform. is ignored.
    min_frequency : None
        Is ignored.
    max_categories : int, default=None
        The maximum number of categories to encode. If None, defaults to 50.

    """
    def __init__(self, *, categories='auto', handle_unknown='ignore', min_frequency=None, max_categories=None):
        MAX_LENGTH_CATEGORIES = 50
        assert (categories == "auto") or (isinstance(categories,list)
                                          and (len(categories)<=MAX_LENGTH_CATEGORIES)
                                          and all([isinstance(x,str) for x in categories]))
        assert handle_unknown == "ignore"
        assert min_frequency == None
        assert (max_categories is None) or (isinstance(max_categories,int) and (max_categories <= MAX_LENGTH_CATEGORIES))

        if max_categories is None:
            max_categories = MAX_LENGTH_CATEGORIES

        self.kind = 'auto'
        self.values = []
        self.max_categories = max_categories

        if isinstance(categories,list):
            self.kind = 'custom'
            self.values = categories

        self._output_col_formula = None
        self._output_col_name = None

        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "OneHotEncoder"

    def define_necessary_statistics(self):
        if  self.kind == 'custom':
            return []
        else:
            return [("TOP", self.max_categories)]

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                         fitted_statistics: dict) -> list[str]:

        output_col_formula = []
        output_col_name = []

        for (prev_col_name_internal, prev_col_name) in zip(prev_col_names_internal, prev_col_names):

            if self.kind == 'custom':
                categories_list = self.values
            else:
                categories_list = fitted_statistics[prev_col_name]['top']

            sql_list_tuples = multicol.one_hot_encoder(prev_col_name_internal, prev_col_name, categories_list)

            [col_formula, col_name ] = [list(t) for t in zip(*sql_list_tuples)]

            output_col_formula += col_formula
            output_col_name += col_name


        self._output_col_formula = output_col_formula
        self._output_col_name = output_col_name

        return self._output_col_formula

    def needs_subquery(self):
        return True

    def are_output_columns_different(self):
        return True

    def get_output_tdtype(self, input_tdtype = None) -> str:
        return "INTEGER()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        #generate_sql_columns must be called first
        assert self._output_col_name is not None
        return self._output_col_name

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return ["INTEGER()" for i in range(len(self._output_col_name))]



class MultiLabelBinarizer(Preprocessor):
    """
    MultiLabelBinarizer for categorical features. The input column is a delimiter separated list of values. The output
    is one indicator variable per unique value.

    Parameters
    ----------
    classes : None, 'auto' or list of str, default=None
        Categories to encode. 'auto' means that categories will be inferred from
        the training data. A list of categories can also be provided.
    sparse_output: boolean, default=False
        Is ignored.
    max_categories : int, default=None
        The maximum number of categories to encode. If None, defaults to 50.
    delimiter : str, default ", "
        The delimiter used to separate the values
    """
    def __init__(self, *, classes=None, sparse_output= False, max_categories=None, delimiter=", "):
        MAX_LENGTH_CATEGORIES = 50
        assert (classes is None) or (classes == "auto") or (isinstance(classes,list)
                                          and (len(classes)<=MAX_LENGTH_CATEGORIES))
        assert sparse_output == False
        assert (max_categories is None) or (isinstance(max_categories,int) and (max_categories <= MAX_LENGTH_CATEGORIES))
        assert isinstance(delimiter,str) and (len(delimiter)>0)

        if max_categories is None:
            max_categories = MAX_LENGTH_CATEGORIES


        self.kind = 'auto'
        self.values = []
        self.max_categories = max_categories
        self.delimiter = delimiter

        if isinstance(classes,list):
            self.kind = 'custom'
            self.values = classes

        self._output_col_formula = None
        self._output_col_name = None

        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "MultiLabelBinarizer"

    def define_necessary_statistics(self):
        if self.kind == 'custom':
            return []
        else:
            return [("TOP_TOKEN", self.max_categories, self.delimiter)]

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                         fitted_statistics: dict) -> list[str]:

        output_col_formula = []
        output_col_name = []

        for (prev_col_name_internal, prev_col_name) in zip(prev_col_names_internal, prev_col_names):

            if self.kind == 'custom':
                categories_list = self.values
            else:
                categories_list = fitted_statistics[prev_col_name]['top_token']

            sql_list_tuples = multicol.multi_label_binarizer(prev_col_name_internal, prev_col_name, categories_list,
                                                             self.delimiter)

            [col_formula, col_name ] = [list(t) for t in zip(*sql_list_tuples)]

            output_col_formula += col_formula
            output_col_name += col_name


        self._output_col_formula = output_col_formula
        self._output_col_name = output_col_name

        return self._output_col_formula

    def needs_subquery(self):
        return True

    def are_output_columns_different(self):
        return True

    def get_output_tdtype(self, input_tdtype = None) -> str:
        return "INTEGER()"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        #generate_sql_columns must be called first
        assert self._output_col_name is not None
        return self._output_col_name

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return ["INTEGER()" for i in range(len(self._output_col_name))]
