"""This module contains functions for writing data mappings to files."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy import Table


def write_as_dict(data: dict[Table, list[dict[str, Any]]], path: str) -> None:
    """Write a data mapping to a file."""

    with open(path, "w") as file:
        for table, value_list in data.items():
            file.write(f"{table.name} = {value_list}\n")


def write_as_sql(data: dict[Table, list[dict[str, Any]]], path: str) -> None:
    """Write a datamapping as raw SQL `INSERT` statements."""

    with open(path, "w") as file:
        for table, data_list in data.items():
            value_list = []
            for data_map in data_list:
                values = []
                for item in data_map.values():
                    if item is None:
                        value = "NULL"
                    elif isinstance(item, str):
                        value = f"""'{item.replace("'", "''")}'"""
                    elif isinstance(item, date | bool):
                        value = f"'{item}'"
                    else:
                        value = str(item)
                    values.append(value)
                value_list.append(f'    ({", ".join(values)})')
            value_string = ",\n".join(value_list)
            file.write(
                f"""\nINSERT INTO "{table.name}" ({", ".join(data_list[0].keys())})\nVALUES\n{value_string};\n"""
            )
