from ._preprocessing import Preprocessor

from ..sql.generator import singlecol


class SimpleHashEncoder(Preprocessor):
    """
    Encodes a single text based column with td-built-in hashfunction to an INTEGER value.
    Stateless and hence very performant, but can lead to collisions.

    Parameters
    ----------
    num_buckets : str, optional
        The number of buckets built on top of the hash code using the modulo operator,
        If None, no the hashvalue is taken without bucketisation.
        Valid options are None or integer.
    salt : str, optional
        a piece of text that is appended at the end of each value. Leads to redistribution of the values to hashvalues.

    Raises
    ------
    AssertionError
        If num_buckets is not one of the allowed values, or if the salt parameter is not valid.

    Notes
    -----
    This class inherits from the Preprocessor abstract class and implements its abstract methods.
    """

    def __init__(self, num_buckets=None, salt=""):
        assert (num_buckets is None) or (isinstance(num_buckets, int) and num_buckets > 1)
        assert  (salt is None) or isinstance(salt, str)

        self.num_buckets = num_buckets
        self.salt = salt
        self.necessary_statistics = self.define_necessary_statistics()

    def __str__(self):
        return "SimpleHashEncoder"

    def define_necessary_statistics(self):
        return []

    def generate_sql_columns(self, prev_col_names_internal: list[str], prev_col_names: list[str],
                             fitted_statistics: dict) -> list[str]:

        # 1. call sql generate function
        sql_list = [singlecol.simple_hash_encoder_str(prev_col_name_internal, self.num_buckets, self.salt )
                    for prev_col_name_internal  in prev_col_names_internal ]
        return sql_list

    def get_output_tdtype(self, input_tdtype = None) -> str:
        return "INTEGER"

    def generate_column_output_names(self, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return []

    def generate_column_output_tdtypes(self, input_tdtypes, fitted_statistics: dict) -> list[str]:
        #important only for those functions where are_output_columns_different == True
        return input_tdtypes