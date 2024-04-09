from ._utils import truncate_float, truncate_float_args

@truncate_float_args
def impute_num(previous_str: str, new_val: float) -> str:
    """
    Returns a SQL expression to impute a numerical column with a missing or null value.

    Parameters
    ----------
    previous_str : str
        The SQL expression that represents the previous value of the column, which can be NULL or missing.
    new_val : float
        The value to use for imputing the missing or null value.

    Returns
    -------
    str
        A SQL expression that represents the imputed value. This expression uses the COALESCE function, which
        returns the first non-null value in a list of expressions. The imputed value is the result of applying
        COALESCE to `previous_str` and `new_val`.

    """
    new_val = truncate_float(new_val)
    return f"COALESCE( {previous_str} , {new_val} )"

def impute_str(previous_str: str, new_val: str) -> str:
    """
    Returns a SQL expression to impute a string column with a missing or null value.

    Parameters
    ----------
    previous_str : str
        The SQL expression that represents the previous value of the column, which can be NULL or missing.
    new_val : str
        The value to use for imputing the missing or null value.

    Returns
    -------
    str
        A SQL expression that represents the imputed value. This expression uses the COALESCE function, which
        returns the first non-null value in a list of expressions. The imputed value is the result of applying
        COALESCE to `previous_str` and `new_val`.
    """
    return f"COALESCE( {previous_str} , '{new_val}' )"

def trycast(previous_str: str, new_type: str) -> str:
    """
    Returns a SQL expression to cast a text column to a new data type and handle any conversion errors.

    Parameters
    ----------
    previous_str : str
        The SQL expression that represents the previous value of the column.
    new_type : str
        The name of the new data type to cast the column to.

    Returns
    -------
    str
        A SQL expression that represents the casted value. This expression uses the TRYCAST function, which
        tries to convert the input value to the specified data type and returns NULL if the conversion fails.
        The casted value is the result of applying TRYCAST to `previous_str` and `new_type`.
    """
    return f"TRYCAST( ({previous_str}) AS {new_type} )"

@truncate_float_args
def scale(previous_str: str, numerator_subtr: float, denominator: float, zerofinull = True) -> str:
    """
    Returns a SQL expression to scale a numeric column by subtracting a numerator and dividing by a denominator.

    Parameters
    ----------
    previous_str : str
        The SQL expression that represents the previous value of the column.
    numerator_subtr : float
        The value to subtract from the numerator of the scaling operation.
    denominator : float
        The value to divide the result of the subtraction by.
    zerofinull: bool, default True
        If the output should be 0 if the division would return null

    Returns
    -------
    str
        A SQL expression that represents the scaled value. This expression uses the ZEROIFNULL and NULLIF
        functions, which set the value to 0 if it is NULL and return 0 if the denominator is 0, respectively.
        The scaled value is the result of subtracting `numerator_subtr` from `previous_str`, dividing the result
        by `denominator`, and applying the ZEROIFNULL and NULLIF functions.

    """

    if zerofinull:
        return f"ZEROIFNULL( (( {previous_str} ) - {numerator_subtr} ) / NULLIF( {denominator} , 0) )"
    else:
        return f" ( ( {previous_str} )  - {numerator_subtr} ) / NULLIF( {denominator} , 0) "

@truncate_float_args
def cutoff(previous_str: str, cutoff_min: float = None, cutoff_max: float = None) -> str:
    """
    Returns a SQL expression that applies cutoffs to a numeric column.

    Parameters
    ----------
    previous_str : str
        The SQL expression that represents the previous value of the column.
    cutoff_min : float, optional
        The minimum value to set the column to, by default None.
    cutoff_max : float, optional
        The maximum value to set the column to, by default None.

    Returns
    -------
    str
        A SQL expression that represents the cutoff value. This expression uses the CASE WHEN function to
        apply the cutoffs specified in `cutoff_min` and `cutoff_max`. If both `cutoff_min` and `cutoff_max`
        are specified, the result of the expression is the value of `previous_str` if it is between `cutoff_min`
        and `cutoff_max`, `cutoff_min` if it is less than `cutoff_min`, and `cutoff_max` if it is greater than
        `cutoff_max`. If only `cutoff_min` is specified, the result of the expression is the value of `previous_str`
        if it is greater than `cutoff_min`, and `cutoff_min` otherwise. If only `cutoff_max` is specified, the
        result of the expression is the value of `previous_str` if it is less than `cutoff_max`, and `cutoff_max`
        otherwise.
    """
    assert( not( (cutoff_min is None) & (cutoff_max is None) ))
    if not( (cutoff_min is None) | (cutoff_max is None) ):
        assert (cutoff_max > cutoff_min)
        return (f"CASE WHEN {previous_str} > {cutoff_max} THEN {cutoff_max} ELSE CASE WHEN {previous_str} < {cutoff_min} THEN {cutoff_min} ELSE {previous_str} END END")
    elif cutoff_min is not None:
        return (f"CASE WHEN {previous_str} < {cutoff_min} THEN {cutoff_min} ELSE {previous_str} END")
    elif cutoff_max is not None:
        return (f"CASE WHEN {previous_str} > {cutoff_max} THEN {cutoff_max} ELSE {previous_str} END")

@truncate_float_args
def fixed_width_binning(previous_str: str, n_bins: int, c_max: float, c_min: float) -> str:
    """
    Discretizes a numerical feature into `n_bins` equal-width bins between `c_min` and `c_max`.

    Parameters
    ----------
    previous_str: str :
        A string representing the name of the input feature.
    n_bins: int :
        An integer specifying the number of bins.
    c_max: float :
        A float representing the maximum value of the feature.
    c_min: float :
        A float representing the minimum value of the feature.

    Returns
    -------
    str :
        A string representing the SQL query for discretizing the input feature into `n_bins` equal-width bins.

    """

    # Scale the input feature to [0,1] using min-max scaling
    min_max_scale_str = scale(previous_str, c_min, c_max-c_min)

    # Bin the feature by computing the bin index (0 to n_bins-1)
    return f"TD_SYSFNLIB.GREATEST( 0 , TD_SYSFNLIB.LEAST({n_bins-1}, CAST( ({min_max_scale_str})  * {n_bins} AS INTEGER)))"

@truncate_float_args
def threshold_binarizer(previous_str: str, threshold: float) -> str:
    """
    Converts a numerical feature into a binary feature based on a given threshold.
    If the input column is greater than the threshold, it returns 1, 0 otherwise.

    Parameters
    ----------
    previous_str: str :
        A string representing the name of the input feature.
    threshold: float :
        A float representing the threshold value for binarization.

    Returns
    -------
    str :
        A string representing the SQL query for binarizing the input feature based on the given threshold.

    """
    return f"CASE WHEN ({previous_str}) > {threshold} THEN 1 ELSE 0 END"

def list_binarizer(previous_str: str, classes_1: list[str]) -> str:
    """
    Converts a text feature into a binary feature based on a list of classes.
    If the input column is an element of the list, it returns 1, 0 otherwise.
    Parameters
    ----------
    previous_str: str :
        A string representing the name of the input feature.
    classes_1: list[str] :
        A list of strings representing the classes to be binarized.

    Returns
    -------
    str :
        A string representing the SQL query for binarizing the input feature based on the given list of classes.

    """
    class_list = ",".join("'" + cl + "'" for cl in classes_1)
    return f"CASE WHEN ({previous_str}) IS IN ({class_list}) THEN 1 ELSE 0 END"

def variable_width_binning(previous_col: str, bin_boundaries: list[float]) -> str:
    """
    Returns a SQL statement that bins a numerical column into discrete categories, based on variable width binning.
    Suitable for quantile binning or defined bin boundaries.

    Parameters
    ----------
    previous_col: str :
        The name of the column to be binned.

    bin_boundaries: list[float] :
        A list of bin boundaries that define the upper bounds of each bin. The number of bins is equal to the length of
        this list plus one.

    Returns
    -------
    str:
        A SQL statement that bins the column according to the provided bin boundaries.
    """
    # suitable for quantile binning, or defined bin boundaries
    bin_boundaries = [truncate_float(bin_) for bin_ in bin_boundaries]

    when_thens = []
    for i, boundary  in enumerate(bin_boundaries):
        when_thens += [f"    WHEN {previous_col} < {boundary} THEN {i}"]
    when_thens_else_end = ["CASE"] + when_thens + [f"    ELSE {len(bin_boundaries)} END"]
    when_thens_else_end_str = " ".join(when_thens_else_end)
    return when_thens_else_end_str

def label_encoder(previous_col: str, classes: list[str]) -> str:
    """
    Returns SQL code to apply label encoding on the specified column.

    Parameters
    ----------
    previous_col : str
        The name of the column to encode.
    classes : list of str
        A list of unique values to be encoded.

    Returns
    -------
    str
        The SQL code to apply label encoding.

    Notes
    -----
    This function assumes that the values in `classes` are sorted in descending order of frequency.

    Examples
    --------
    >>> classes = ['dog', 'cat', 'mouse']
    >>> previous_col = 'animals'
    >>> label_encoder_str = label_encoder(previous_col, classes)
    CASE animals
        WHEN 'dog' THEN 1
        WHEN 'cat' THEN 2
        WHEN 'mouse' THEN 3
        ELSE 0
    END

    """
    #annahme, values in classes absteigend nach häufigkeit sortiert
    num_value_range = list(range(1, len(classes) + 1))
    col_wt_list = []
    for i, val in zip(num_value_range, classes):
        wt = f"""WHEN '{val}' THEN {i}"""
        col_wt_list.append(wt)
    all_cwte = " ".join( [f"CASE {previous_col}"] + col_wt_list + [f"""ELSE 0 END """])
    return all_cwte

def custom_transformation(previous_col: str, transformation: str) -> str:
    """
        Apply a custom transformation to a column.

        Parameters
        ----------
        previous_col : str
            The name of the column to be transformed.
        transformation : str
            A string representing the transformation to be applied to the column.
            The string should contain the substring '%%COL%%' where the column
            values should be inserted.

        Returns
        -------
        str
            The transformed column values as a string.

        Notes
        -----
        This function applies a custom transformation to a column based on a string
        provided by the user. It is intended for advanced users who have a deep
        understanding of SQL and the implications of custom transformations.

        The `transformation` parameter should be a string that specifies the desired
        transformation using SQL syntax. The string should include the substring
        '%%COL%%' where the column values should be inserted. For example, the
        following transformation would multiply the column values by 2:

        "2 * %%COL%%"

        Use this function with caution as it may produce unexpected results or
        introduce errors in your data.

        Examples
        --------
        >>> custom_transformation('column_name', '2 * %%COL%%')
        "2 * column_name"
        """
    #use at own risk
    assert ('%%COL%%' in transformation)
    transf_ = transformation.replace('%%COL%%', f"( {previous_col} )")
    return transf_

@truncate_float_args
def scaleminmax(previous_str: str, numerator_subtr: float, denominator: float, zerofinull: bool,
                                             feature_range: tuple, clip: bool ) -> str:
    feature_range_min = feature_range[0]
    feature_range_max = feature_range[1]
    feature_range_width = feature_range_max - feature_range_min

    scale_str = scale(previous_str, numerator_subtr, denominator, zerofinull)

    rescaled_scale_str = f" ( ({scale_str}) * {feature_range_width} + {feature_range_min})"
    if clip:
        rescaled_scale_str = f"TD_SYSFNLIB.LEAST( TD_SYSFNLIB.GREATEST( {rescaled_scale_str}, {feature_range_min}) , {feature_range_max}) "
    return rescaled_scale_str


def simple_hash_encoder_str(previous_str: str, num_buckets: int, salt: str) -> str:
    """

    """
    mod1_str, mod2_str, salt_str = "","",""
    if num_buckets is not None:
        mod1_str, mod2_str = "MOD(", f",{num_buckets})"
    if (salt is not None) and  (len(salt)>0):
        salt_str = f" ||'{salt}'"

    return f"{mod1_str}ABS(CAST(FROM_BYTES(HASHROW({previous_str}{salt_str}),'base10') AS INTEGER)){mod2_str}"


def cast(previous_str: str, new_type: str) -> str:
    """
    Returns a SQL expression to cast a column to a new data type. Does not handle conversion errors

    Parameters
    ----------
    previous_str : str
        The SQL expression that represents the previous value of the column.
    new_type : str
        The name of the new data type to cast the column to.

    Returns
    -------
    str
        A SQL expression that represents the casted value. This expression uses the TRYCAST function, which
        tries to convert the input value to the specified data type and returns NULL if the conversion fails.
        The casted value is the result of applying TRYCAST to `previous_str` and `new_type`.
    """
    return f"CAST( ({previous_str}) AS {new_type} )"


@truncate_float_args
def power_transform_yeojohnson(previous_str: str, lambda_: float) -> str:
    colname = previous_str
    formula_lt0 = ""
    formula_gte0 = ""

    if lambda_ == 0:
        formula_lt0 = f"-(POWER(-{colname} + 1,2-({lambda_}))-1)/(2-({lambda_}))"
        formula_gte0 = f"LN({colname} + 1)"
    elif lambda_ == 2:
        formula_lt0 = f"-LN(-{colname} + 1)"
        formula_gte0 = f"(POWER({colname} + 1 ,{lambda_})-1)/({lambda_})"
    else:
        formula_lt0 = f"-(POWER(-{colname} + 1,2-({lambda_}))-1)/(2-({lambda_}))"
        formula_gte0 = f"(POWER({colname} + 1 ,{lambda_})-1)/({lambda_})"

    return f"CASE WHEN {colname} >= 0.0 THEN {formula_gte0} ELSE {formula_lt0} END"

@truncate_float_args
def power_transform_boxcox(previous_str: str, lambda_: float) -> str:
    colname = previous_str
    formula = ""
    if lambda_ == 0:
        formula = f"LN({colname})"
    else:
        formula = f"(POWER({colname}, {lambda_}) - 1) / {lambda_}"
    return f"CASE WHEN {colname} > 0.0 THEN {formula} ELSE NULL END"









