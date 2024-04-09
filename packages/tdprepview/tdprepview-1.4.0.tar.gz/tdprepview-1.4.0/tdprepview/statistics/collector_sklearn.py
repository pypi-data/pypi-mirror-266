import pandas as pd
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.decomposition import PCA
from sklearn.preprocessing import PowerTransformer

from sklearn.experimental import enable_iterative_imputer # noqa
from sklearn.impute import IterativeImputer

def get_imperativeimputer_params(df_sampled: pd.DataFrame, columns: list[str]):
    df_data = df_sampled[columns]

    imp_mean = IterativeImputer(random_state=0, max_iter=1)
    imp_mean.fit(df_data)

    regression_weights = {idx:list(est.coef_)  for (idx, _, est) in imp_mean.imputation_sequence_}
    intercepts =         {idx:est.intercept_   for (idx, _, est) in imp_mean.imputation_sequence_}
    means = {idx:mean_ for (idx,mean_) in zip(list(range(len(columns))), imp_mean.initial_imputer_.statistics_ )}

    return_dict = {}
    for idx, col in enumerate(columns):
        return_dict[col] = {}
        return_dict[col]["mean"] = means[idx]
        return_dict[col]["intercept"] = intercepts[idx]
        return_dict[col]["regression_weights"] = regression_weights[idx]

    return return_dict

def get_pca_loadings(df_sampled: pd.DataFrame, columns,  n_components=  "mle"):
    df_data = df_sampled[columns]

    pca = PCA(n_components, svd_solver="full", random_state = 42)
    pca.fit(df_data)

    return_dict = {"PCA": {}}
    for i, row in enumerate(pca.components_):
        return_dict["PCA"][i + 1] = list(row)

    return return_dict

def get_decisiontree_boundaries(df_sampled: pd.DataFrame, colstats_tree):
    if colstats_tree == []:
        return None
    # structure of colstats_tree:
    # (col, "TREE", target_var, model_type, no_bins )


    splitting_boundaries = {}
    # calculate decision trees
    for (col, _, target_var, model_type, no_bins ) in colstats_tree:
        # initialize empty dictionary to store feature splitting boundaries
        df_train = df_sampled[[col, target_var]].dropna()
        feature_data = df_train[[col]]
        y = df_train[target_var]
        if model_type == "classification":
            clf = DecisionTreeClassifier(random_state=42, max_leaf_nodes=no_bins)
        else:
            # model_type == "regression":
            clf = DecisionTreeRegressor(random_state=42, max_leaf_nodes=no_bins)

        clf.fit(feature_data, y)
        splitting_boundaries[col] = {}
        splitting_boundaries[col]["tree_bins"] = sorted(list(set(clf.tree_.threshold.tolist())))

    return splitting_boundaries

def get_lambdas_power_transformer(df_sampled: pd.DataFrame, columns, method='yeo-johnson'):
    lambdas = {}
    for c in columns:
        pt = PowerTransformer(method=method, standardize=False)
        df_fit = df_sampled[[c]]
        df_fit = df_fit.loc[df_fit[c].notnull()]
        if method == "box-cox":
            df_fit = df_fit.loc[df_fit[c]>0]
        pt.fit(df_fit)
        lambdas[c] = {"lambda":pt.lambdas_[0]}
    return lambdas
