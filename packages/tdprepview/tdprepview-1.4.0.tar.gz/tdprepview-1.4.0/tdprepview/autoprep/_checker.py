# all functions here check the applicability of single Preprocessor on a single Column

def _check_imputation(df, column_name, teradata_dtype):
    """
    Determine the appropriate imputation method for a given column based on its data type and uniqueness.

    Parameters:
    df (DataFrame): The dataframe containing the data.
    column_name (str): The name of the column to impute.
    teradata_dtype (str): The data type of the column in Teradata database terms.

    Returns:
    dict: A dictionary containing the imputation method and its parameters.
    """
    teradata_dtype = teradata_dtype.split("(")[0]
    unique_values = df[column_name].dropna().unique()
    imputation_details = {}

    if teradata_dtype in ['VARCHAR', 'CHAR']:
        imputation_details['preprocessor'] = 'ImputeText'
        imputation_details['parameters'] = {'kind': 'mode'}
    elif len(unique_values) == 2:
        imputation_details['preprocessor'] = 'SimpleImputer'
        imputation_details['parameters'] = {'strategy': 'most_frequent'}
    elif teradata_dtype in ['BIGINT', 'FLOAT']:
        imputation_details['preprocessor'] = 'SimpleImputer'
        imputation_details['parameters'] = {'strategy': 'mean'}
    else:
        imputation_details['preprocessor'] = 'Impute'
        imputation_details['parameters'] = {'kind': 'mode'}

    return imputation_details


def _check_powertransformer(df, column_name, teradata_dtype):
    """
    Check whether a PowerTransformer is applicable for a given column based on its data type and skewness.

    Parameters:
    df (DataFrame): The dataframe containing the data.
    column_name (str): The column to evaluate for power transformation.
    teradata_dtype (str): The data type of the column in Teradata database terms.

    Returns:
    dict: A dictionary containing the PowerTransformer and its parameters if applicable, empty otherwise.
    """
    teradata_dtype = teradata_dtype.split("(")[0]
    preprocessor_details = {}
    unique_values = df[column_name].dropna().unique()

    if len(unique_values) > 2 and teradata_dtype in ['BIGINT', 'FLOAT']:
        skewness = df[column_name].skew()
        if abs(skewness) > 0.5:
            preprocessor_details['preprocessor'] = 'PowerTransformer'
            preprocessor_details['parameters'] = {'method': 'yeo-johnson'}

    return preprocessor_details


def _check_minmaxscaling(df, column_name, teradata_dtype):
    """
    Determine if MinMax scaling is needed for a column based on its data type and uniqueness.

    Parameters:
    df (DataFrame): The dataframe containing the data.
    column_name (str): The column to evaluate for MinMax scaling.
    teradata_dtype (str): The data type of the column in Teradata database terms.

    Returns:
    dict: A dictionary containing the MinMaxScaler and its parameters if applicable, empty otherwise.
    """
    teradata_dtype = teradata_dtype.split("(")[0]
    preprocessor_details = {}
    unique_values = df[column_name].dropna().unique()

    if len(unique_values) > 2 and teradata_dtype in ['BIGINT', 'FLOAT']:
        preprocessor_details['preprocessor'] = 'MinMaxScaler'
        preprocessor_details['parameters'] = {}

    return preprocessor_details


def _check_textencoding(df, column_name, teradata_dtype):
    """
    Determine the text preprocessing requirements for a given column based on its data type and uniqueness.

    Parameters:
    df (DataFrame): The dataframe containing the data.
    column_name (str): The column to evaluate for text preprocessing.
    teradata_dtype (str): The data type of the column in Teradata database terms.

    Returns:
    dict: A dictionary containing the text preprocessor and its parameters if applicable, empty otherwise.
    """
    teradata_dtype = teradata_dtype.split("(")[0]
    preprocessor_details = {}
    unique_values = df[column_name].dropna().unique()

    if teradata_dtype in ['CHAR', 'VARCHAR']:
        delimiter = ','
        multi_label_count = df[column_name].dropna().apply(lambda x: delimiter in str(x)).sum()

        if multi_label_count > 0.1 * len(df):
            preprocessor_details['preprocessor'] = 'MultiLabelBinarizer'
            preprocessor_details['parameters'] = {"delimiter": ",", "max_categories": 20}
        elif len(unique_values) > 2:
            preprocessor_details['preprocessor'] = 'OneHotEncoder'
            preprocessor_details['parameters'] = {"max_categories": 20}
        else:
            preprocessor_details['preprocessor'] = 'LabelEncoder'
            preprocessor_details['parameters'] = {"elements": "TOP1"}

    return preprocessor_details