import teradataml as tdml
from packaging import version

# Package colors provides the list of standard terminal color codes.
class bcolors:
	ResetAll = "\033[0m"

	Bold       = "\033[1m"
	Dim        = "\033[2m"
	Underlined = "\033[4m"
	Blink      = "\033[5m"
	Reverse    = "\033[7m"
	Hidden     = "\033[8m"

	ResetBold       = "\033[21m"
	ResetDim        = "\033[22m"
	ResetUnderlined = "\033[24m"
	ResetBlink      = "\033[25m"
	ResetReverse    = "\033[27m"
	ResetHidden     = "\033[28m"

	Default      = "\033[39m"
	Black        = "\033[30m"
	Red          = "\033[31m"
	Green        = "\033[32m"
	Yellow       = "\033[33m"
	Blue         = "\033[34m"
	Magenta      = "\033[35m"
	Cyan         = "\033[36m"
	LightGray    = "\033[37m"
	DarkGray     = "\033[90m"
	LightRed     = "\033[91m"
	LightGreen   = "\033[92m"
	LightYellow  = "\033[93m"
	LightBlue    = "\033[94m"
	LightMagenta = "\033[95m"
	LightCyan    = "\033[96m"
	White        = "\033[97m"

	BackgroundDefault      = "\033[49m"
	BackgroundBlack        = "\033[40m"
	BackgroundRed          = "\033[41m"
	BackgroundGreen        = "\033[42m"
	BackgroundYellow       = "\033[43m"
	BackgroundBlue         = "\033[44m"
	BackgroundMagenta      = "\033[45m"
	BackgroundCyan         = "\033[46m"
	BackgroundLightGray    = "\033[47m"
	BackgroundDarkGray     = "\033[100m"
	BackgroundLightRed     = "\033[101m"
	BackgroundLightGreen   = "\033[102m"
	BackgroundLightYellow  = "\033[103m"
	BackgroundLightBlue    = "\033[104m"
	BackgroundLightMagenta = "\033[105m"
	BackgroundLightCyan    = "\033[106m"
	BackgroundWhite        = "\033[107m"

def is_version_greater_than(tested_version, base_version="17.20.00.03"):
    """
    Author of this function: Denis Molin

    Check if the tested version is greater than the base version.

    This function compares two version numbers, the 'tested_version' and the 'base_version',
    to determine if the 'tested_version' is greater. It uses Python's `version.parse` function
    to perform the comparison.

    Args:
        tested_version (str): Version number to be tested.
        base_version (str, optional): Base version number to compare. Defaults to "17.20.00.03".

    Returns:
        bool: True if the 'tested_version' is greater than the 'base_version', False otherwise.

    Example:
        To check if a version is greater than the default base version:
        >>> is_greater = is_version_greater_than("17.20.00.04")

        To check if a version is greater than a custom base version:
        >>> is_greater = is_version_greater_than("18.10.00.01", base_version="18.00.00.00")

    """
    return version.parse(tested_version) > version.parse(base_version)

def execute_query(query):
    """
    Execute a SQL query or a list of queries using the tdml module.

    This function checks the version of the tdml module and executes the query or queries accordingly.
    For versions greater than 17.20.00.03, it uses `tdml.execute_sql`; otherwise, it uses `tdml.get_context().execute`.

    Args:
        query (str or list): A single SQL query string or a list of SQL query strings.

    Returns:
        The result of the SQL execution if a single query is passed. None if a list of queries is passed or an exception occurs.

    Example:
        To execute a single SQL query and retrieve the result:
        >>> result = execute_query("SELECT * FROM my_table")

        To execute a list of SQL queries:
        >>> execute_query(["UPDATE table1 SET column1 = 42", "DELETE FROM table2 WHERE condition"])

    Note:
        - If a single query is passed, the function returns the result of the SQL execution.
        - If a list of queries is passed, the function executes each query and returns None.
        - If an exception occurs during execution, the error message and the problematic query are printed,
          and the function returns None.

    """
    # Check if the version of tdml is greater than the specified base version
    if is_version_greater_than(tdml.__version__, base_version="17.20.00.03"):
        # If query is a list, iterate and execute each query
        if type(query) == list:
            for q in query:
                try:
                    tdml.execute_sql(q)  # Execute the query
                except Exception as e:
                    # Print the first line of the exception and the query that caused it
                    print(str(e).split('\n')[0])
                    print(q)
        else:
            # If query is not a list, execute it and return the result
            try:
                return tdml.execute_sql(query)
            except Exception as e:
                # Print the first line of the exception and the query
                print(str(e).split('\n')[0])
                print(query)
    else:
        # For tdml versions not greater than the specified version
        if type(query) == list:
            for q in query:
                try:
                    # Use the older execution method for the query
                    tdml.get_context().execute(q)
                except Exception as e:
                    # Print the first line of the exception and the query
                    print(str(e).split('\n')[0])
                    print(q)
        else:
            try:
                # Execute the single query using the older method and return the result
                return tdml.get_context().execute(query)
            except Exception as e:
                # Print the first line of the exception and the query
                print(str(e).split('\n')[0])
                print(query)

    # No return value if a list of queries is executed or if an exception occurs
    return


