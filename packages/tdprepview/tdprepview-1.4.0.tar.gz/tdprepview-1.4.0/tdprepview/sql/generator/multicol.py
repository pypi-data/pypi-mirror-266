import re
import pandas as pd
import uuid

from ._utils import truncate_float, truncate_float_args

def dimensionality_reduction(previous_cols: list[str], column_names: list[str], factor_loadings_dict:dict) -> list[str]:
    # same for PCA, FA ....

    return_list = []
    for i, (_, factor_loadings) in enumerate(factor_loadings_dict.items()):
        products_= [f"({truncate_float(factor)}) * ({feat})" for (factor, feat) in zip(factor_loadings,previous_cols)]
        sum_ = "  +  ".join(products_)
        return_list.append(sum_)

    return return_list


def iterative_imputer(previous_cols: list[str], column_names: list[str], means: dict,
                      intercepts: dict, regression_weights: dict) -> list[str]:

    # enforces subquery
    initial_imputes = [f"COALESCE({col_int}, {truncate_float(means[col])})" for col_int, col
                       in zip(previous_cols, column_names)]

    return_list = []
    for col_int, col in zip(previous_cols, column_names):
        b0 = truncate_float(intercepts[col])
        feature_list = [init_imp for init_imp,x in zip(initial_imputes,previous_cols) if (x != col_int)]

        products_ = [f"({truncate_float(b1)}) * ({feat})" for (b1, feat) in zip(regression_weights[col], feature_list)]
        sum_ = "  +  ".join([str(b0)] + products_)
        coalesce = f"COALESCE( {col_int}, {sum_} )"
        return_list.append(coalesce)

    return return_list


def polynomial_features(previous_col_list: list[str], column_name_list: list[str], degree :int, interaction_only = False):
    from sklearn.preprocessing import PolynomialFeatures
    pf = PolynomialFeatures(degree=degree, interaction_only=interaction_only, include_bias=False, order='C')
    df = pd.DataFrame([list(range(1,1+len(previous_col_list)))], columns=previous_col_list)
    pf.fit(df)

    return_values = []
    new_formulas = pf.get_feature_names_out()
    for formula in new_formulas:
        col_formula = formula.replace("^","**").replace(" "," * ")
        new_col_name = col_formula.replace(" * ", "__").replace("**", "_")
        for (internal, external) in zip(previous_col_list, column_name_list):
            new_col_name     =     new_col_name.replace(internal, external)

        return_values.append((col_formula,new_col_name))

    return return_values


def normalize(previous_col_list: str, column_name_list: str,
              norm: str = "l2") -> list[str]:
    assert norm in ["max", "l1", "l2"]

    return_list = []

    denominator_col = "denominator" + str(uuid.uuid4()).replace("-", "")[:5]

    denominator = ""
    if norm == "l1":
        denominator = "(" + " + ".join([f"ABS({c})" for c in previous_col_list]) + ")"
    elif norm == "l2":
        denominator = "SQRT(" + " + ".join([f"({c})**2" for c in previous_col_list]) + ")"
    elif norm == "max":
        assert (len(previous_col_list) <= 10)
        denominator = "TD_SYSFNLIB.GREATEST(" + ", ".join([f"ABS({c})" for c in previous_col_list]) + ")"

    for i, (prev_col, col_name) in enumerate(zip(previous_col_list, column_name_list)):
        new_col = f"({prev_col}) / {denominator_col}"
        if i == 0:
            # this is a little trick, to help optimise the query
            new_col = f"{denominator} AS {denominator_col}, " + new_col
        return_list.append(new_col)

    return return_list


def one_hot_encoder(previous_col: str, column_name: str, categories_list: list[str]) -> list[tuple]:
    """
    One-hot encode a categorical column.

    Parameters
    ----------
    previous_col : str
        The name of the previous column in the one-hot encoding process.
    column_name : str
        The name of the categorical column to be encoded.
    categories_list : list of str
        A list of categories in the categorical column.

    Returns
    -------
    list of tuples
        A list of tuples containing the encoded column expressions and the new column names.
        Each tuple has two elements:
            - The first element is a SQL expression for the encoded column.
            - The second element is a string with the new column name.

    """

    # annahme, values in classes absteigend nach häufigkeit sortiert
    num_value_range = list(range(1, len(categories_list) + 1))
    return_list = []


    pattern_colname = "[^a-zA-Z0-9_]"
    for i, cat in zip(num_value_range, categories_list):
        col_cwte = f"CASE {previous_col} WHEN '{cat}' THEN 1 ELSE 0 END "
        # get column name
        new_column_name = column_name + f"__OHE_{i}"
        cleaned_cat = re.sub(pattern_colname, "", cat)
        new_column_name += "_" + cleaned_cat
        return_list.append((col_cwte, new_column_name))

    # otherwise case:
    categories_str = ", ".join([f"'{cat}'" for cat in categories_list])
    col_cwte = f"CASE WHEN ({previous_col}) IS NOT IN ({categories_str}) THEN 1 ELSE 0 END "
    new_column_name = column_name + f"__OHE_0_otherwise"
    return_list.append((col_cwte, new_column_name))

    return return_list



def multi_label_binarizer(previous_col: str, column_name: str, categories_list: list[str], delimiter: str) -> list[tuple]:
    """
    multi label binarize a categorical column with many values separated by a delimiter.

    Parameters
    ----------
    previous_col : str
        The name of the previous column in the one-hot encoding process.
    column_name : str
        The name of the categorical column to be encoded.
    categories_list : list of str
        A list of categories in the categorical column.
    delimiter:
        delimiter

    Returns
    -------
    list of tuples
        A list of tuples containing the encoded column expressions and the new column names.
        Each tuple has two elements:
            - The first element is a SQL expression for the encoded column.
            - The second element is a string with the new column name.

    """

    # annahme, values in classes absteigend nach häufigkeit sortiert
    num_value_range = list(range(1, len(categories_list) + 1))
    return_list = []

    pattern = "[^a-zA-Z0-9_]"
    for i, cat in zip(num_value_range, categories_list):
        pos_expression = f"POSITION('{delimiter}{cat}{delimiter}' IN '{delimiter}'||{previous_col}||'{delimiter}')"
        col_cwte = f"CASE WHEN ({pos_expression})>0 THEN 1 ELSE 0 END"
        # get column name
        new_column_name = column_name + f"__MLB_{i}"
        cleaned_cat = re.sub(pattern, "", cat)
        new_column_name += "_" + cleaned_cat

        return_list.append((col_cwte, new_column_name))

    return return_list