from ._preprocessing import Preprocessor

from ..sql.generator import singlecol


class TryCast(Preprocessor):
    """
    A preprocessor that attempts to convert a text column to a new data type using SQL TRYCAST function.

    Parameters
    ----------
    new_type : str
        The new data type to attempt to cast the column to. Must be one of the following: 'BYTEINT', 'SMALLINT', 'INT',
        'BIGINT', 'FLOAT', 'DATE', 'TIME', 'TIMESTAMP(6)'.

    Raises
    ------
    AssertionError
        If new_type is not one of the allowed values.

    Notes
    -----
    This class inherits from the Preprocessor abstract class and implements its abstract methods.
    """
    def __init__(self, new_type="FLOAT"):
        assert(new_type in ["BYTEINT","SMALLINT", "INT", "BIGINT", "FLOAT", "DATE", "TIME", "TIMESTAMP(6)"])
        self.new_type = new_type
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "TryCast"

    def define_necessary_statistics(self):
        return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:

        # 2. call sql generate function
        sql_list = [singlecol.trycast(prev_col_name_internal, new_type = self.new_type)  for
                    prev_col_name_internal in prev_col_names_internal ]
        return sql_list

    def get_output_tdtype(self, input_tdtype = None) -> str:
        return self.new_type

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return [self.new_type for _ in input_tdtypes]


class Cast(Preprocessor):
    """
    A preprocessor that converts a column to a new data type using SQL CAST function.
    It will be mostly useful to transform all features into FLOAT as last preprocessing step.
    If the input columns are text based, it is safer to use TryCast.

    Parameters
    ----------
    new_type : str
        The new data type to attempt to cast the column to. Must be one of the following: 'BYTEINT', 'SMALLINT', 'INT',
        'BIGINT', 'FLOAT', 'DATE', 'TIME', 'TIMESTAMP(6)'. Default 'FLOAT'

    Raises
    ------
    AssertionError
        If new_type is not one of the allowed values.

    Notes
    -----
    This class inherits from the Preprocessor abstract class and implements its abstract methods.
    """
    def __init__(self, new_type="FLOAT"):
        assert(new_type in ["BYTEINT","SMALLINT", "INT", "BIGINT", "FLOAT", "DATE", "TIME", "TIMESTAMP(6)"])
        self.new_type = new_type
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "Cast"

    def define_necessary_statistics(self):
        return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:

        # 2. call sql generate function
        sql_list = [singlecol.cast(prev_col_name_internal, new_type = self.new_type)  for
                    prev_col_name_internal in prev_col_names_internal ]
        return sql_list

    def get_output_tdtype(self, input_tdtype = None) -> str:
        return self.new_type

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return [self.new_type for _ in input_tdtypes]
