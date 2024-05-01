"""main."""

from typing import Any

from pyvis.network import Network


def get_node_name(_class: Any) -> str:  # noqa: ANN401
    """Get node name from a class.

    Args:
        _class (Any): Class to get node name from.

    Returns:
        str: Node name.
    """
    return f"{_class.__name__} {_class.__module__}"


def scan_objects(start: object, excluded_objects: tuple[object]) -> dict[str, set[object]]:
    """Scan objects.

    Args:
        start (object): Object to start scanning from.
        excluded_objects (tuple[object]): Objects to exclude from scanning.

    Returns:
        dict[str, set[object]]: Object relationships.
    """
    objects_to_scan: set[object] = {start}
    classes: dict[str, set[object]] = {}
    while objects_to_scan:
        current_class: Any = objects_to_scan.pop()
        if current_class in (excluded_objects):
            continue
        subclasses: set[object] = set(current_class.__subclasses__())
        objects_to_scan.update(subclasses)

        classes[get_node_name(current_class)] = subclasses

    return classes


def add_node_wrapper(
    graph: Network,
    node_name: str,
    class_module: str,
    color: str,
) -> None:
    """Add node to graph.

    Args:
        graph (Network): Graph to add node to.
        node_name (str): Node name.
        class_module (str): Class module.
        color (str): Node color.
    """
    graph.add_node(
        node_name,
        color=color,
        mass=5,
        module=class_module,
        type="branch",
    )


def map_objects(
    graph: Network,
    parent: str,
    classes: set[object],
    object_relationships: dict[str, set[object]],
    layer: int,
) -> None:
    """Map objects.

    Args:
        graph (Network): Graph to map objects to.
        parent (str): Parent node name.
        classes (set[object]): Classes to map.
        object_relationships (dict[str, set[object]]): Object relationships.
        layer (int): Layer of the graph.
    """
    colors = ["blue", "purple"]
    for _class in classes:
        subclass_module = _class.__module__
        subclass_node_name = get_node_name(_class)
        add_node_wrapper(
            graph=graph,
            node_name=subclass_node_name,
            class_module=subclass_module,
            color=colors[layer % len(colors)],
        )
        graph.add_edge(parent, subclass_node_name)

        subclasses = object_relationships[subclass_node_name]
        if subclasses:
            map_objects(
                graph=graph,
                parent=subclass_node_name,
                classes=subclasses,
                object_relationships=object_relationships,
                layer=layer + 1,
            )
        else:
            graph.get_node(subclass_node_name)["color"] = "red"


def object_mapper(start: object, object_relationships: dict[str, set[object]]) -> None:
    """Object mapper.

    Args:
        start (object): Start object.
        object_relationships (dict[str, set[object]]): Object relationships.
    """
    graph = Network(
        directed=True,
        select_menu=True,
        filter_menu=True,
        height="1000px",
        width="100%",
    )
    center_module = start.__module__
    center_node_name = get_node_name(start)
    add_node_wrapper(graph, center_node_name, center_module, "green")

    map_objects(
        graph=graph,
        parent=center_node_name,
        classes=object_relationships[center_node_name],
        object_relationships=object_relationships,
        layer=0,
    )

    graph.save_graph("nx_big.html")


def main() -> None:
    """Main."""
    start = object
    excluded_objects = (type(type),)
    object_relationships = scan_objects(start, excluded_objects)

    # THIS IS A HACK BECAUSE TYPES ARE ANNOYING
    object_relationships["type builtins"] = set()

    object_mapper(start, object_relationships)

    print("Done")


if __name__ == "__main__":
    main()
