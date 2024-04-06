from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal
from uuid import UUID, uuid4

from sqlalchemy import inspect
from sqlalchemy.orm import KeyFuncDict

if TYPE_CHECKING:
    from sqlalchemy import Table
    from sqlalchemy.orm import DeclarativeBase, Relationship

__all__ = ["SQLAlchemyFlattener"]


class SQLAlchemyFlattener:
    def __init__(
        self,
        id_attribute_name: str = "id",
        id_attribute_type: Literal["uuid"] = "uuid",  # TODO: Add BigInt support
        serialize_uuids: bool = True,
        serialize_dates: bool = True,
        use_enum_values: bool = True,
        generate_secondary_id: bool = True,
    ) -> None:
        """Initialize a flattener instance.

        Args:
            id_attribute_name: The name of the primary key attribute.
            id_attribute_type: The primary key value type.
            serialize_uuids: Whether to serialize UUIDs to strings.
            serialize_dates: Whether to serialize dates to strings.
            use_enum_values: Whether to use enum values instead of enum names.
            generate_secondary_id: Whether to generate a primary key ID for secondary tables.
        """
        self.id_attribute_name = id_attribute_name
        self.id_attribute_type = id_attribute_type
        self.serialize_uuids = serialize_uuids
        self.serialize_dates = serialize_dates
        self.use_enum_values = use_enum_values
        self.generate_secondary_id = generate_secondary_id

    def flatten(
        self,
        data: DeclarativeBase | Sequence[DeclarativeBase],
    ) -> dict[Table, list[dict[str, Any]]]:
        """Flatten SQLAlchemy models to dictionaries ready for bulk insertion."""

        if not isinstance(data, Sequence):
            data = [data]

        data_map = {}
        for model in data:
            data_map = self.flatten_instance(model, data_map)

        return self.deduplicate_data_mapping(data_map)

    def flatten_instance(
        self, instance: DeclarativeBase, data_map: dict[Table, list[dict[str, Any]]]
    ) -> dict[Table, list[dict[str, Any]]]:
        """Flatten SQLAlchemy models to dictionaries ready for bulk insertion."""

        inspector = inspect(instance)
        self._append_mapping(data_map, instance.__table__, self.convert(instance))

        for relationship in inspector.mapper.relationships:
            if relationship.uselist:
                collection = getattr(instance, relationship.key)
                if isinstance(collection, KeyFuncDict):
                    collection = collection.values()
                for child in collection:
                    if relationship.secondary is not None:
                        secondary_dict = self.generate_secondary_row(
                            relationship, instance, child
                        )
                        # check that the secondary row is not already present - ID values could be random
                        if not (
                            secondary_records := data_map.get(relationship.secondary)
                        ) or not any(
                            {
                                k: v
                                for k, v in secondary_dict.items()
                                if k != self.id_attribute_name
                            }
                            == {
                                k: v
                                for k, v in record.items()
                                if k != self.id_attribute_name
                            }
                            for record in secondary_records
                        ):
                            self._append_mapping(
                                data_map, relationship.secondary, secondary_dict
                            )
                    # avoid infinite recursion when circular references are present
                    if (entries := data_map.get(child.__table__)) and any(
                        str(entry.get("id")) == str(child.id) for entry in entries
                    ):
                        continue
                    # recursive flattening
                    data_map = self.flatten_instance(child, data_map)

            else:
                if (child := getattr(instance, relationship.key)) is not None:
                    # avoid infinite recursion when circular references are present
                    if (entries := data_map.get(child.__table__)) and any(
                        str(entry.get("id")) == str(child.id) for entry in entries
                    ):
                        continue
                    data_map = self.flatten_instance(child, data_map)

        return data_map

    def generate_secondary_row(
        self,
        relationship: Relationship,
        parent: DeclarativeBase,
        child: DeclarativeBase,
    ) -> dict[str, Any]:
        """Generate rows for secondary a.k.a. association tables."""
        secondary_dict = {}
        for column in relationship.remote_side:
            foreign_key = next(iter(column.foreign_keys))
            secondary_dict[column.name] = (
                getattr(parent, foreign_key.column.name)
                if foreign_key.column.table == parent.__table__
                else getattr(child, foreign_key.column.name)
            )
            if self.serialize_uuids and isinstance(secondary_dict[column.name], UUID):
                secondary_dict[column.name] = str(secondary_dict[column.name])
        if self.generate_secondary_id:
            secondary_dict[self.id_attribute_name] = (
                str(uuid4()) if self.serialize_uuids else uuid4()
            )

        return secondary_dict

    def _append_mapping(
        self,
        data_map: dict[Table, list[dict[str, Any]]],
        table: Table,
        data_row: dict[str, Any],
    ) -> Any:
        if table not in data_map:
            data_map[table] = []
        data_map[table].append(data_row)
        return data_map

    def convert(self, instance: DeclarativeBase) -> dict[str, Any]:
        """Convert a SQLAlchemy model instance data to key value pairs as a dictionary."""

        inspector = inspect(instance)

        mapping: dict[str, str | Enum | date | UUID] = {}
        for column in inspector.mapper.column_attrs:
            value = getattr(instance, column.key)
            if self.use_enum_values and isinstance(value, Enum):
                mapping[column.expression.key] = value.value
                continue
            if self.serialize_dates and isinstance(value, date):
                mapping[column.expression.key] = str(value)
                continue
            if self.serialize_uuids and isinstance(value, UUID):
                mapping[column.expression.key] = str(value)
                continue

            mapping[column.expression.key] = value

        return mapping

    def deduplicate_data_mapping(
        self,
        data_map: dict[Table, list[dict[str, Any]]],
    ) -> dict[Table, list[dict[str, Any]]]:
        """Deduplicate data mapping values."""

        return {
            table: [dict(t) for t in {tuple(d.items()) for d in values}]
            for table, values in data_map.items()
        }
