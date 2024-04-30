"""main."""

from pprint import pprint

from pyvis.network import Network


def get_node_name(node: object) -> str:
    return f"{node.__name__} {node.__module__}"


def scan_objects(start: object) -> dict[str, set[object]]:
    objects_to_scan: set[object] = {start}
    classes: dict[str, set[object]] = {}
    while objects_to_scan:
        current_class = objects_to_scan.pop()
        try:
            subclasses: set[object] = set(current_class.__subclasses__())
        except Exception as error:
            pprint(f"Error: {error}")
            continue
        objects_to_scan.update(subclasses)

        classes[get_node_name(current_class)] = subclasses

    return classes


def add_node_wrapper(
    graph: Network,
    node_name: str,
    class_module: str,
    color: str,
    physics: bool = True,  # noqa: FBT001, FBT002 I dont see a readable way to fix these errors
):
    """Add node to graph."""
    graph.add_node(
        node_name,
        color=color,
        mass=10,
        module=class_module,
        physics=physics,
        type="branch",
    )


def map_objects(
    graph: Network,
    parent: str,
    classes: set[object],
    object_relationships: dict[str, set[object]],
    layer: int,
) -> None:
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
    graph = Network(
        directed=True,
        select_menu=True,
        filter_menu=True,
        height="1000px",
        width="100%",
    )
    center_module = start.__module__
    center_node_name = get_node_name(start)
    add_node_wrapper(graph, center_node_name, center_module, "green", physics=False)

    map_objects(
        graph=graph,
        parent=center_node_name,
        classes=object_relationships[center_node_name],
        object_relationships=object_relationships,
        layer=0,
    )

    print("Saving graph to nx_big.html")
    graph.save_graph("nx_big.html")
    print("Done")


def main() -> None:
    start = object

    object_relationships = scan_objects(start)

    # THIS IS A HACK BECAUSE TYPES ARE ANNOYING
    object_relationships["type builtins"] = set()

    object_mapper(start, object_relationships)


if __name__ == "__main__":
    main()
