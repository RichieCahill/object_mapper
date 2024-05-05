"""main."""

import logging
from json import loads
from pathlib import Path

from pyvis.network import Network


def add_node_wrapper(
    graph: Network,
    node_name: str,
    color: str,
) -> None:
    """Add node to graph.

    Args:
        graph (Network): Graph to add node to.
        node_name (str): Node name.
        color (str): Node color.
    """
    graph.add_node(
        n_id=node_name,
        color=color,
        mass=5,
        module=node_name.split(" ")[1],
        base_module=node_name.split(" ")[1].split(".", 1)[0],
        type="branch",
    )


def map_objects(
    graph: Network,
    parent: str,
    subclass_node_names: list[str],
    object_relationships: dict[str, list[str]],
    layer: int,
) -> None:
    """Map objects.

    Args:
        graph (Network): Graph to map objects to.
        parent (str): Parent node name.
        subclass_node_names (list[str]): Subclass node names.
        object_relationships (dict[str, set[object]]): Object relationships.
        layer (int): Layer of the graph.
    """
    colors = ["blue", "purple"]
    for subclass_node_name in subclass_node_names:
        if graph.node_map.get(subclass_node_name):
            graph.add_edge(parent, subclass_node_name)
            continue

        add_node_wrapper(
            graph=graph,
            node_name=subclass_node_name,
            color=colors[layer % len(colors)],
        )
        graph.add_edge(parent, subclass_node_name)

        if subclass_node_names := object_relationships[subclass_node_name]:
            map_objects(
                graph=graph,
                parent=subclass_node_name,
                subclass_node_names=subclass_node_names,
                object_relationships=object_relationships,
                layer=layer + 1,
            )
        else:
            graph.get_node(n_id=subclass_node_name)["color"] = "red"


def object_mapper(start_node_name: str, object_relationships: dict[str, list[str]]) -> None:
    """Object mapper.

    Args:
        start_node_name (str): Starting node name.
        object_relationships (dict[str, set[object]]): Object relationships.
    """
    graph = Network(
        directed=True,
        select_menu=True,
        filter_menu=True,
        height="1000px",
        width="100%",
    )

    add_node_wrapper(graph=graph, node_name=start_node_name, color="green")

    map_objects(
        graph=graph,
        parent=start_node_name,
        subclass_node_names=object_relationships[start_node_name],
        object_relationships=object_relationships,
        layer=0,
    )

    graph.save_graph("nx_big.html")


def main() -> None:
    """Main."""
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting data visualization.")

    object_relationships_file = Path(__file__).parent / "object_relationships.json"
    object_relationships_data = loads(object_relationships_file.read_text())
    object_mapper(
        object_relationships_data["start"],
        object_relationships_data["object_relationships"],
    )

    logging.info("data visualization done.")


if __name__ == "__main__":
    main()
