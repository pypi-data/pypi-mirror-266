from ._DAG import DAG, Node, ColumnNode, PreProcesserNode
from ..preprocessing import *

def _serialize(pipeline):
    # Serialize preprocessors
    preprocessors = [step[1] for step in pipeline.steps]
    preprocessor_serialized = {
        str(id(prep)): {
            "classname": prep.__class__.__name__,
            "attributes": prep.__dict__
        } for prep in preprocessors
    }

    # Serialize nodes
    nodes = pipeline._dag.traverse_breathfirst()
    nodes_serialized = {
        str(id(node)): {
            "classname": node.__class__.__name__,
            "attributes": {
                key: value for key, value in node.__dict__.items()
                if key not in ["prev_nodes", "successor_nodes", "preprocessor"]
            }
        } for node in nodes
    }

    # Serialize DAG
    dag_serialized = {"query": pipeline._dag.query}

    # Serialize Pipeline
    pipeline_serialized = {
        "_is_fitted": pipeline._is_fitted,
        "_needs_DF_for_fitting": pipeline._needs_DF_for_fitting
    }

    # Serialize relationships between objects
    node_to_preprocessor = [
        (str(id(node)), str(id(node.preprocessor)))
        for node in nodes if hasattr(node, "preprocessor")
    ]

    node_to_previous = [
        (str(id(node)), str(id(prev_node)))
        for node in nodes for prev_node in getattr(node, "prev_nodes", [])
    ]

    node_to_successor = [
        (str(id(node)), str(id(succ_node)))
        for node in nodes for succ_node in getattr(node, "successor_nodes", [])
    ]

    dag_to_root_nodes = [str(id(root_node)) for root_node in pipeline._dag.root_nodes]

    steps_to_preprocessor_ids = [(step[0], str(id(step[1])), step[2]) for step in pipeline.steps]

    # Final serialization as a dictionary
    pipeline_serialized = {
        "preprocessors": preprocessor_serialized,
        "nodes": nodes_serialized,
        "dag": dag_serialized,
        "pipeline": pipeline_serialized,
        "node_to_preprocessor": node_to_preprocessor,
        "node_to_previous": node_to_previous,
        "node_to_successor": node_to_successor,
        "dag_to_root_nodes": dag_to_root_nodes,
        "steps_to_preprocessor_ids": steps_to_preprocessor_ids
    }

    return pipeline_serialized


def _read_from_serialized(serialized_data):
    # Extract parts of the serialized data using keys
    preps_serialized = serialized_data["preprocessors"]
    nodes_serialized = serialized_data["nodes"]
    dag_serialized = serialized_data["dag"]
    pipeline_serialized = serialized_data["pipeline"]
    node_to_preprocessor = serialized_data["node_to_preprocessor"]
    node_to_previous = serialized_data["node_to_previous"]
    node_to_successor = serialized_data["node_to_successor"]
    dag_root_nodes = serialized_data["dag_to_root_nodes"]
    steps_to_preprocessor_ids = serialized_data["steps_to_preprocessor_ids"]

    # Reconstruct preprocessors
    preps_obj = {}
    for obj_id, content in preps_serialized.items():
        classname = content["classname"]
        #assert classname in tdprepview.__all__, f"Classname {classname} not found in tdprepview.__all__"
        new_obj = eval(f"{classname}.__new__({classname})")
        new_obj.__dict__.update(content["attributes"])
        preps_obj[obj_id] = new_obj

    # Reconstruct nodes
    nodes_obj = {}
    for obj_id, content in nodes_serialized.items():
        classname = content["classname"]
        assert classname in ["ColumnNode", "PreProcesserNode"], f"Classname {classname} is not a valid Node type"
        new_obj = eval(f"{classname}.__new__({classname})")
        new_obj.__dict__.update(content["attributes"])
        # Initialize lists to avoid missing keys
        new_obj.prev_nodes = []
        new_obj.successor_nodes = []
        if classname == "PreProcesserNode":
            new_obj.preprocessor = None
        nodes_obj[obj_id] = new_obj

    # Reconstruct DAG
    new_DAG = DAG([])
    new_DAG.query = dag_serialized.get("query", None)

    # Reestablish relationships
    for node_id, preprocessor_id in node_to_preprocessor:
        nodes_obj[node_id].preprocessor = preps_obj[preprocessor_id]

    for node_id, prev_node_id in node_to_previous:
        nodes_obj[node_id].prev_nodes.append(nodes_obj[prev_node_id])

    for node_id, succ_node_id in node_to_successor:
        nodes_obj[node_id].successor_nodes.append(nodes_obj[succ_node_id])

    new_DAG.root_nodes = [nodes_obj[node_id] for node_id in dag_root_nodes]

    new_steps = [(step_info[0], preps_obj[step_info[1]], step_info[2]) for step_info in
                          steps_to_preprocessor_ids]


    return new_DAG, pipeline_serialized, new_steps
