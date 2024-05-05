"""main."""

from json import dumps
from pathlib import Path
from typing import Any


def get_node_name(_class: Any) -> str:  # noqa: ANN401
    """Get node name from a class.

    Args:
        _class (Any): Class to get node name from.

    Returns:
        str: Node name.
    """
    return f"{_class.__name__} {_class.__module__}"


def scan_objects(start: object, excluded_objects: tuple[object]) -> dict[str, list[str]]:
    """Scan objects.

    Args:
        start (object): Object to start scanning from.
        excluded_objects (tuple[object]): Objects to exclude from scanning.

    Returns:
        dict[str, set[object]]: Object relationships.
    """
    objects_to_scan: set[object] = {start}
    classes: dict[str, list[str]] = {}
    print(f"Excluding {excluded_objects}")
    while objects_to_scan:
        current_class: Any = objects_to_scan.pop()
        if current_class in (excluded_objects):
            print(f"Excluding {current_class}")
            continue
        subclasses: set[object] = set(current_class.__subclasses__())
        subclasses.difference_update(set(excluded_objects))
        objects_to_scan.update(subclasses)

        classes[get_node_name(current_class)] = [get_node_name(subclass) for subclass in subclasses]

    return classes


def main() -> None:
    """Main."""
    start = object
    excluded_objects = (type(type),)
    object_relationships = scan_objects(start, excluded_objects)

    # THIS IS A HACK BECAUSE TYPES ARE ANNOYING
    object_relationships["type builtins"] = []
    object_relationships_file = Path(__file__).parent / "object_relationships.json"
    object_relationships_file.write_text(
        dumps(
            {
                "start": get_node_name(start),
                "object_relationships": object_relationships,
            },
        ),
    )


if __name__ == "__main__":
    main()
