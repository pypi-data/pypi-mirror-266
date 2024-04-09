from ._preprocessing import Preprocessor
from ..sql.generator import multicol


class PCA(Preprocessor):
    """
    Principal component analysis (PCA) is a technique used to reduce the dimensionality of a dataset while retaining
    most of its variance.

    Parameters
    ----------
    n_components : int or 'mle', optional
        The number of principal components to keep. If 'mle', automatically determines the number of components
        using the MLE (maximum likelihood estimation) method. Default is 'mle'.
    random_state : int, optional
        Seed for the random number generator. Default is 42.

    Returns
    -------
    PCA
        A PCA object that can be used to transform data to a lower dimensional space.

    Raises
    ------
    AssertionError
        If n_components is not an integer or 'mle'.

    Notes
    -----
    This class is based on the PCA class from scikit-learn's decomposition module.

    """

    def __init__(self, n_components='mle', *, random_state=42):
        assert isinstance(n_components, int)  or (n_components  == "mle")
        self.n_components = n_components
        self.random_state = random_state
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return f"PCA"

    def define_necessary_statistics(self):
        return [("PCA", self.n_components)]

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:
        # 1. read relevant values from statistics
        factor_loadings_dict = fitted_statistics["PCA"]

        # 2. call sql generate function
        sql_list = multicol.dimensionality_reduction(prev_col_names_internal, prev_col_names, factor_loadings_dict)

        return sql_list

    def needs_subquery(self):
        return True

    def are_inputs_combined(self):
        return True

    def are_output_columns_different(self):
        return True

    def get_output_tdtype(self, input_tdtype = None) -> str:
        return "FLOAT()"


    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return [f"pc_{i+1}" for i in range(len(fitted_statistics["PCA"]))]

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return [ "FLOAT()" for i in range(len(fitted_statistics["PCA"]))]