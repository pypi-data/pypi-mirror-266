import argparse
import importlib
import sys
from collections.abc import Callable
from pathlib import Path

from sqlalchemy_flattener.flattener import SQLAlchemyFlattener
from sqlalchemy_flattener.writers import write_as_dict, write_as_sql


def main() -> None:
    parser = argparse.ArgumentParser(description="Flatten SQLAlchemy ORM instances.")
    parser.add_argument(
        "instances",
        type=str,
        help="The module namespace containing the model instances, e.g. `foo.bar.instance_list`",
    )
    parser.add_argument(
        "order",
        type=str,
        help="The module namespace containing a sequence of table insert ordering.",
    )
    parser.add_argument(
        "output",
        type=str,
        help="The output file path to write the flattened data to.",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="sql",
        choices=["dict", "sql"],
        help="The format to write the data in.",
    )

    args = parser.parse_args()

    sys.path.append(Path.cwd())
    instance_path, instance_var = args.instances.rsplit(".", 1)
    module = importlib.import_module(instance_path)
    instances = getattr(module, instance_var)
    if isinstance(instances, Callable):
        instances = instances()

    order_path, order_var = args.order.rsplit(".", 1)
    module = importlib.import_module(order_path)
    order = getattr(module, order_var)

    flattener = SQLAlchemyFlattener()
    unordered_data = flattener.flatten(instances)

    ordered_mapping = {
        model.__table__: data
        for model in order
        if (data := unordered_data.get(model.__table__)) is not None
    }

    if args.format == "dict":
        write_as_dict(ordered_mapping, args.output)
    else:
        write_as_sql(ordered_mapping, args.output)


if __name__ == "__main__":
    main()
