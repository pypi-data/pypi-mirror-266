from .collector_vantage import get_numeric_statistics_adapter, get_varchar_statistics_adapter, get_varchar_TOPTOKEN_statistics_adapter
from .collector_sklearn import get_decisiontree_boundaries, get_imperativeimputer_params, get_pca_loadings, get_lambdas_power_transformer

NEED_SAMPLE_LIST = ["PCA","TREE","IterativeImpute","POWER_TRANSFORMER"]
SAMPLE_SIZE = 50000



def _get_columns_for_data_sample(statistics_requirements_):
    columns_ = []
    for _, dict_ in statistics_requirements_.items():
        if any([stats[0] in NEED_SAMPLE_LIST for stats in dict_["required_statistics"]]):
            columns_ += dict_["columns"]
        columns_ += [stats[1] for stats in dict_["required_statistics"] if stats[0]=="TREE"]
    columns_ = list(set(columns_))
    return columns_


def _get_columns_per_statistics(statistics_requirements_):
    columns_per_statistics = {}
    for _, dict_ in statistics_requirements_.items():
        stats_ids = [stats[0] for stats in dict_["required_statistics"]]
        for stat_id in set(stats_ids) - set(columns_per_statistics.keys()):
            columns_per_statistics[stat_id] = {"columns": [], "settings": []}

        for stat_id in stats_ids:
            new_columns = [c for c in dict_["columns"] if c not in columns_per_statistics[stat_id]["columns"]]
            columns_per_statistics[stat_id]["columns"] += new_columns

            new_settings = [setting for setting in dict_["required_statistics"] if setting[0] == stat_id]
            new_settings = [s for s in new_settings if s not in columns_per_statistics[stat_id]["settings"]]
            columns_per_statistics[stat_id]["settings"] += new_settings

    return columns_per_statistics

def _get_all_columns_from_requirements(statistics_requirements):
    columns_ = []
    for _, dict_ in statistics_requirements.items():
        columns_ += dict_["columns"]
    columns_ = list(dict.fromkeys(columns_))
    return columns_

def _calculate_statistics_update_dict(statistics_requirements, statistics_collected, DF_dag, df_dag, stat_id, setting):

    # 1. get all statisctis and put in in one single dict
    all_columns = _get_all_columns_from_requirements(statistics_requirements)
    all_stats = {col:{} for col in all_columns}
    if stat_id == "numstat":
        new_stats = get_numeric_statistics_adapter( DF_dag, setting, all_columns)
    elif stat_id ==  "TOP" :
        new_stats = get_varchar_statistics_adapter(DF_dag, setting)
    elif stat_id == "PCA":
        new_stats = get_pca_loadings(df_dag, columns = setting["columns"],  n_components=  setting["settings"][0][1])
    elif stat_id == "TREE":
        colstats_tree = [(col,) + setting["settings"][0] for col in setting["columns"]]
        new_stats = get_decisiontree_boundaries(df_dag, colstats_tree)
    elif stat_id == "IterativeImpute":
        columns = setting["columns"]
        new_stats = get_imperativeimputer_params(df_dag, columns)
    elif stat_id == "TOP_TOKEN":
        new_stats = get_varchar_TOPTOKEN_statistics_adapter(DF_dag, setting)
    elif stat_id == "POWER_TRANSFORMER":
        columns = setting["columns"]
        method = setting["settings"][0][1]
        new_stats = get_lambdas_power_transformer(df_dag, columns = columns, method = method)
    else:
        return

    # example of new_stats content:
    # { "f8":{
    #           "mean":22, "max":44, "median":20, "P10":10, "P90":42},
    #   "PCA": {
    #           0:[-2,2.3,4.2], 1:[-2,2.3,4.2]}}

    # browse through statistics_requirements and assign statistics_collected values as in all_stats
    # statistics_collected = {node_id:{} for node_id, _ in statistics_requirements.items()}

    for node_id in statistics_requirements.keys():
        for col_or_statid in new_stats.keys():
            if col_or_statid not in statistics_collected[node_id].keys():
                statistics_collected[node_id][col_or_statid] = new_stats[col_or_statid]
            else: #already exists
                statistics_collected[node_id][col_or_statid].update(new_stats[col_or_statid])







def collect_statistics_by_requirements(DF_dag, statistics_requirements):

    statistics_collected = {node_id:{} for node_id, _ in statistics_requirements.items()}
    if DF_dag is None:
        return statistics_collected

    #check if any step needs the sample
    columns_sample = _get_columns_for_data_sample(statistics_requirements)
    df_dag = None
    if len(columns_sample)>0:
        df_dag = DF_dag.sample(n=SAMPLE_SIZE, randomize=True).select(columns_sample).to_pandas(all_rows=True)

    columns_per_statistics = _get_columns_per_statistics(statistics_requirements)

    for stat_id, setting in columns_per_statistics.items():
        if stat_id not in ["standard","median","P"]:
            _calculate_statistics_update_dict(statistics_requirements,statistics_collected, DF_dag, df_dag, stat_id, setting)

    #combine for num_stats (Special Case)
    if len(set(columns_per_statistics.keys()) & set(["standard", "median", "P"])) > 0:
        num_stat_settings = {key: val for key, val in columns_per_statistics.items() if key in ["standard","median","P"]}
        if num_stat_settings.keys() != []:
            _calculate_statistics_update_dict(statistics_requirements, statistics_collected, DF_dag, df_dag, "numstat", num_stat_settings)

    return statistics_collected

