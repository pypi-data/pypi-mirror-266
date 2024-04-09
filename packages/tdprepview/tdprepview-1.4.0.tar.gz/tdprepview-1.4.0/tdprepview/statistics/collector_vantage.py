import pandas as pd
import teradataml as tdml
from numpy import dtype

def get_numeric_statistics(DF:tdml.DataFrame, cols_standard, cols_median_percentile, centiles)  -> pd.DataFrame:
    # tdml.UnivariateStatistics requires Database Version >= 17.10.x.x

    res_df = pd.DataFrame({'ATTRIBUTE': pd.Series(dtype=dtype('O')),
                       'StatName': pd.Series(dtype=dtype('O')),
                       'StatValue': pd.Series(dtype=dtype('float64'))})

    if (cols_standard is not None) and len(cols_standard)>0:
        try:
            df_stats1 = tdml.UnivariateStatistics(
                newdata = DF,
                target_columns=cols_standard,
                stats=["MEAN","MAX","MIN","MODE","STD"]
                ).result.to_pandas()
        except:
            DF_limited = DF.select(cols_standard)
            DF_limited.to_sql("inbetweenres", temporary=True, if_exists="replace")
            DF_limited = tdml.DataFrame("inbetweenres")
            df_stats1 = tdml.UnivariateStatistics(
                newdata=DF_limited,
                target_columns=cols_standard,
                stats=["MEAN", "MAX", "MIN", "MODE", "STD"]
            ).result.to_pandas()

        res_df = pd.concat([res_df, df_stats1])

    if (cols_median_percentile is not None) and len(cols_median_percentile)>0:
        if centiles == []:
            centiles = [50]

        try:
            df_stats2 = tdml.UnivariateStatistics(
                newdata=DF,
                target_columns=cols_median_percentile,
                stats=["MEAN","MAX","MIN","MODE","STD", "MEDIAN", "PERCENTILES"],
                centiles=centiles,
                ).result.to_pandas()
        except:
            DF_limited = DF.select(cols_median_percentile)
            DF_limited.to_sql("inbetweenres", temporary=True, if_exists="replace")
            DF_limited = tdml.DataFrame("inbetweenres")
            df_stats2 = tdml.UnivariateStatistics(
                newdata=DF_limited,
                target_columns=cols_median_percentile,
                stats=["MEAN","MAX","MIN","MODE","STD", "MEDIAN", "PERCENTILES"],
                centiles=centiles,
                ).result.to_pandas()

        res_df = pd.concat([res_df, df_stats2])

    #translate strings for statistics into compatible names
    res_df["StatName"] = res_df["StatName"].str.lower()
    translation_dict = {
        "minimum":"min",
        "maximum":"max",
        "standard deviation":"std",
    }
    for i in range(0,100):
        translation_dict[f"percentiles({i})"] = f"P{i}"
    res_df = res_df.replace({"StatName": translation_dict})

    return res_df


def get_numeric_statistics_adapter(DF_dag,  setting, all_columns):
    # 1.transform input values
    cols_standard = []
    cols_median_percentile = []
    centiles = []
    for _, set_settings in setting.items():
        if any([stat[0] in ["P","median"] for stat in set_settings["settings"]]):
            cols_median_percentile += list(set_settings["columns"])
            new_centiles = [stat[1] for stat in set_settings["settings"] if stat[0] == "P"]
            centiles += new_centiles

    cols_median_percentile = list(set(cols_median_percentile))
    centiles = list(set(centiles))
    cols_standard = list(set(all_columns)-set(cols_median_percentile))

    #2. call function
    res_df = get_numeric_statistics(DF_dag, cols_standard, cols_median_percentile, centiles)

    # evtl todo: StatName umbennenen --> PERCENTILE90 zu P90, usw.

    # 3. transform table to dict
    def create_dict(df):
        dict_ = {}
        for _, row in df.iterrows():
            attribute = row['ATTRIBUTE']
            stat_name = row['StatName']
            stat_value = row['StatValue']
            if attribute not in dict_:
                dict_[attribute] = {}
            dict_[attribute][stat_name] = stat_value
        return dict_

    ret_dict = create_dict(res_df)

    return ret_dict


def get_varchar_statistics(DF:tdml.DataFrame, col_maxtop_dict:dict)  -> dict:

    if col_maxtop_dict == {}:
        # no statistics needed
        return {}

    DF._DataFrame__execute_node_and_set_table_name(DF._nodeid, DF._metaexpr)
    view_name = DF._table_name

    list_pddfs = []
    for colname, colcount in col_maxtop_dict.items():
        query = f"""
            SELECT
                '{colname}' as ColumnName,
                 {colname} as DistinctValue,
                COUNT(*) as DistinctValueCount,
                RANK() OVER (ORDER BY DistinctValueCount DESC) as DistinctValueCountRank
            FROM
                {view_name}
            GROUP BY 
                DistinctValue
            WHERE
                {colname} IS NOT NULL
            QUALIFY 
                (DistinctValueCountRank <= {colcount})
        """

        col_pddf = tdml.DataFrame.from_query(query).to_pandas()
        list_pddfs.append(col_pddf)

    df_res = pd.concat(list_pddfs)

    return df_res.groupby('ColumnName')['DistinctValue'].apply(list).to_dict()


def get_varchar_statistics_adapter(DF_dag, setting):
    # e.g. setting = {'columns': {'f1', 'f2', 'f8'}, 'settings': {('TOP', 2)} }

    # 1. transform input
    maxtop = list(setting['settings'])[0][1]
    col_maxtop_dict = {col:maxtop  for col in setting['columns']}

    # 2. call function
    df_res_dict = get_varchar_statistics(DF_dag, col_maxtop_dict)

    # 3. transform output
    res_dict = {}
    for col, value_list in df_res_dict.items():
        res_dict[col] = {}
        res_dict[col]["top"] = value_list

    return res_dict


def get_varchar_TOPTOKEN_statistics(DF:tdml.DataFrame, col_maxtop_dict:dict, delimiter:str)  -> dict:


    if col_maxtop_dict == {}:
        # no statistics needed
        return {}

    DF._DataFrame__execute_node_and_set_table_name(DF._nodeid, DF._metaexpr)
    view_name = DF._table_name

    return_dict = {}
    for colname, num_top_token in col_maxtop_dict.items():

        query = f"""
                    SELECT 
                        {colname} as list_value,
                        COUNT(*) as num_list
                    FROM 
                        {view_name}
                    GROUP BY
                        {colname}
                    WHERE
                        {colname} IS NOT NULL
        """
        df_dist = tdml.DataFrame.from_query(query).to_pandas()
        df_dist["values_split"] = df_dist.list_value.str.split(delimiter)
        exploded_df = df_dist[["num_list", "values_split"]].explode('values_split')
        top_values = (exploded_df
                         .groupby("values_split")
                         .agg({"num_list":"sum"})
                         .reset_index()
                         .sort_values("num_list", ascending=False)
                        .head(num_top_token)
                    ).values_split.tolist()
        return_dict[colname] = top_values

    return return_dict


def get_varchar_TOPTOKEN_statistics_adapter(DF_dag, setting):
    # e.g. setting = {'columns': {'f1', 'f2', 'f8'}, 'settings': {('TOP_TOKEN', 50, ", ")} }

    # 1. transform input
    maxtop = list(setting['settings'])[0][1]
    delimiter = list(setting['settings'])[0][2]
    col_maxtop_dict = {col:maxtop  for col in setting['columns']}

    # 2. call function
    df_res_dict = get_varchar_TOPTOKEN_statistics(DF_dag, col_maxtop_dict, delimiter)

    # 3. transform output
    res_dict = {}
    for col, value_list in df_res_dict.items():
        res_dict[col] = {}
        res_dict[col]["top_token"] = value_list

    return res_dict




