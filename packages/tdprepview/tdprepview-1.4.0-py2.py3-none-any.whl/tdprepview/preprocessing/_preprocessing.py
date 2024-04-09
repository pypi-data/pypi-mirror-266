from abc import abstractmethod


class Preprocessor:
    """
    Abstract base class for data preprocessing operations. Subclasses should implement
    the abstract methods `define_necessary_statistics()` and `generate_sql_column()`.

    Methods
    -------
    define_necessary_statistics()
        Abstract method to define necessary statistics for preprocessing.

    generate_sql_column(previous_str: str, column_name: str, statistics_num: str, statistics_varchar: str) -> str
        Abstract method to generate SQL column for preprocessing.

    needs_subquery() -> bool
        Returns False as preprocessing does generally not require a subquery. Needs to be overwritten by Subclass
        if necessary.
    """

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def define_necessary_statistics(self):
        pass

    @abstractmethod
    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str], fitted_statistics: dict) -> list[str]:
        pass

    def needs_subquery(self):
        return False

    def are_inputs_combined(self):
        """
        True, if multiple input columns are combined to new columns (e.g. PolynomialFeatures, PCA, IterativeImputer)
        False, if (multiple) input columns are treated independently (e.g. Impute, OneHotEncoding, )
        --> 1 Preprocessing node or k preprocessing nodes
        :return:
        :rtype: bool
        """
        return False

    def are_output_columns_different(self):
        """
        False, if always for one input column, one column will be output (e.g. Impute, IterativeImputer, Scale)
        True, if output columns can vary or are indpendent of number of input columns,
                            (e.g. OneHotEncoding, PCA, PolynomialFeatures, Concat, MultiColSum)
        :return:
        :rtype: bool
        """
        return False

    @abstractmethod
    def get_output_tdtype(self, input_tdtype=None) -> str:
        # for those functions where are_output_columns_different == False
        pass

    @abstractmethod
    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        pass

    @abstractmethod
    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        pass

    # @abstractmethod
    # def is_reversable(self) -> bool:
    #     pass
    #
    # @abstractmethod
    # def generated_reverse_column(self) -> list[str]:
    #     pass








