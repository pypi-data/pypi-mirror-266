
def _is_valid_str_percentile(p_string):
    """
    Check if a string has the format 'P[0-100]'

    :param p_string: The string to check
    :type p_string: str
    :return: True if the string has the format 'P[0-100]', False otherwise
    :rtype: bool
    """
    if len(p_string) < 2:
        return False
    if p_string[0] != 'P':
        return False
    try:
        number = int(p_string[1:])
        if 0 <= number <= 100:
            return True
        else:
            return False
    except ValueError:
        return False

def _is_valid_str_top(top_string):
    """
    Check if a string has the format 'TOP[0-10000]'

    :param top_string: The string to check
    :type top_string: str
    :return: True if the string has the format 'TOP[0-10000]', False otherwise
    :rtype: bool
    """
    if len(top_string) < 4:
        return False
    if top_string[:3] != 'TOP':
        return False
    try:
        number = int(top_string[3:])
        if 1 <= number <= 10000:
            return True
        else:
            return False
    except ValueError:
        return False

def _get_val_statistics(statistics_num, column_name, statistic ):
    # match name accordingly
    new_statname  = statistic
    if statistic.startswith("PERCENTILE"):
        new_statname = statistic.replace("PERCENTILE","PERCENTILES(") + ")"
    elif statistic.lower() in ["min", "max", "std","mean","median","mode"]:
        replacement_dict = {
                "min": "MINIMUM",
                "max": "MAXIMUM",
                "std": "STANDARD DEVIATION",
                "mean": "MEAN",
                "median": "MEDIAN",
                "mode": "MODE"
        }
        new_statname = replacement_dict[statistic.lower()]
    filtered_statistics = statistics_num.loc[
        (statistics_num.ATTRIBUTE == column_name) &
        (statistics_num.StatName == new_statname.upper())]
    assert(len(filtered_statistics)==1)
    return filtered_statistics["StatValue"].values[0]


