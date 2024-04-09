from ._DAG import DAG, Node, ColumnNode, PreProcesserNode


def _get_color_preprocessor(preproc_str):
    import seaborn as sns
    N_COLORS = 60
    colors_hex = list(sns.color_palette("hls", N_COLORS).as_hex())
    colormapping = {
        "Impute": colors_hex[0],
        'ImputeText': colors_hex[1],
        'SimpleImputer': colors_hex[2],
        'IterativeImputer': colors_hex[3],

        'Scale': colors_hex[10],
        'StandardScaler': colors_hex[11],
        'MaxAbsScaler': colors_hex[12],
        'MinMaxScaler': colors_hex[13],
        'RobustScaler': colors_hex[14],
        'CutOff': colors_hex[15],
        'CustomTransformer': colors_hex[16],
        'Normalizer': colors_hex[17],
        'PowerTransformer': colors_hex[18],

        'FixedWidthBinning': colors_hex[20],
        'VariableWidthBinning': colors_hex[21],
        'QuantileTransformer': colors_hex[22],
        'DecisionTreeBinning': colors_hex[23],
        'ThresholdBinarizer': colors_hex[24],
        'Binarizer': colors_hex[25],
        'ListBinarizer': colors_hex[26],
        'LabelEncoder': colors_hex[27],

        'PolynomialFeatures': colors_hex[30],
        'OneHotEncoder': colors_hex[31],
        'MultiLabelBinarizer': colors_hex[32],

        'PCA': colors_hex[40],

        'TryCast': colors_hex[50],
        'Cast': colors_hex[51],

        'SimpleHashEncoder': colors_hex[55],
    }
    return colormapping.get(preproc_str, "red")


def _get_data_from_dag(dag:DAG):
    labels, colors = [], []
    source, target = [], []

    node_list = dag.traverse_depthfirst()

    for node in node_list:
        if isinstance(node, ColumnNode):
            labels.append(node.column_name)
            colors.append("blue")
        else:
            labels.append(str(node.preprocessor))
            color_ = _get_color_preprocessor(str(node.preprocessor))
            colors.append(color_)

    for prev_node in node_list:
        for suc_node in prev_node.successor_nodes:
            source.append(node_list.index(prev_node))
            target.append(node_list.index(suc_node))
        if (prev_node in dag.root_nodes) and (len(prev_node.successor_nodes) == 0):
            # column that is not processed:
            labels.append(prev_node.column_name)
            colors.append("blue")
            source.append(node_list.index(prev_node))
            target.append(len(labels) - 1)

    value = [1 for _ in source]
    return labels, colors, source, target, value

def plot_dag_pipeline(dag):

    try:
        import seaborn as sns
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError("Plotting the Sankey diagram requires plotly and seaborn. "
                          "Please install them using `pip install seaborn plotly`.")


    labels, colors, source, target, value = _get_data_from_dag(dag)

    fig = go.Figure(data=[go.Sankey(
        arrangement='perpendicular',
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=colors
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        ))])

    fig.update_layout(title_text="Data Preprocessing Pipeline", font_size=10)

    return fig