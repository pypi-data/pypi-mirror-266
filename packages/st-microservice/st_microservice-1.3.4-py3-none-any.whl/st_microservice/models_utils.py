from abc import ABC
from typing import TypeVar, Callable, Awaitable, dataclass_transform
from dataclasses import is_dataclass, field, fields, Field

from graphql import GraphQLResolveInfo
import pypika
from pypika.queries import QueryBuilder


class ValueEnum:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__(self, item):
        return self.__dict__[item]

    def __getitem__(self, item):
        return self.__dict__[item]


class Registry:
    def __init__(
            self,
            query_class: type[pypika.Query] = pypika.Query,
            schema_name: str | None = None,
            custom_loader: Callable[[GraphQLResolveInfo, QueryBuilder], Awaitable[list]] | None = None
    ):
        self.schema_name = schema_name
        self.models = []
        self.custom_loader = custom_loader
        self.query_class = query_class


class ModelMetaData:
    def __init__(
            self,
            registry: Registry,
            table_name: str,
            primary_keys: list[str],
            table: pypika.Table,
            dataclass_fields: dict[str, Field],
            database_fields: dict[str, pypika.Field]
    ):
        self.registry = registry
        self.table_name = table_name
        self.primary_keys = primary_keys
        self.table = table
        self.dataclass_fields = dataclass_fields
        self.database_fields = database_fields
        self.database_fields_list = list(database_fields.values())

        self.relations: dict[str, Relation] = {}
        self.field_count = len(self.database_fields)


class BaseModel(ABC):
    __metadata__: ModelMetaData


T = TypeVar('T', bound=BaseModel)


@dataclass_transform()
def database_model(
        registry: Registry,
        table_name: str,
        primary_keys: list[str],
):
    def database_model_sub(cls: type[T]) -> type[T]:
        assert is_dataclass(cls)

        # Collect Fields
        dc_fields = fields(cls)

        assert issubclass(cls, BaseModel)  # Need to be after fields(cls)

        # Check primary keys
        for pk in primary_keys:
            if pk not in [f.name for f in dc_fields]:
                raise TypeError(f"primary key column '{pk}' not found in {cls.__name__}")

        database_table = pypika.Table(table_name, registry.schema_name)

        # Build fields
        dataclass_fields = {}
        database_fields = {}
        for dc_field in dc_fields:
            field_name = dc_field.name
            db_real_name = dc_field.metadata.get('db_name', field_name)
            # Todo: Make sure works when aliasing
            table_field = pypika.Field(db_real_name, field_name if field_name != db_real_name else None, database_table)
            setattr(cls, field_name, table_field)  # After dataclass processing, reset class attibutes
            dataclass_fields[field_name] = dc_field
            database_fields[field_name] = table_field

        metadata = ModelMetaData(registry, table_name, primary_keys, database_table, dataclass_fields, database_fields)

        cls.__metadata__ = metadata

        # Add to registry
        registry.models.append(cls)

        return cls
    return database_model_sub


class Relation:
    def __init__(self, model: type[BaseModel], rel_model: type[BaseModel],  join_on: dict[str, pypika.Field]):
        self.model = model
        self.rel_model = rel_model
        self.join_on = join_on

        self.rel_table = rel_model.__metadata__.table
        self.on_criterion = pypika.Criterion.all([
            rel_field == getattr(model, main_field_name)
            for main_field_name, rel_field in join_on.items()
        ])


def setup_relation(model: type[BaseModel], relation_name: str, rel_model: type[BaseModel], **join_on):
    assert len(join_on) > 0
    assert model.__metadata__.registry is rel_model.__metadata__.registry

    main_field_names = model.__metadata__.database_fields.keys()
    ref_fields = rel_model.__metadata__.database_fields.values()

    for main_field_name, ref_field in join_on.items():
        if main_field_name not in main_field_names:
            raise Exception(f"Main field {main_field_name} does not exist in {model.__name__} "
                            f"for relation {relation_name}")
        if ref_field not in ref_fields:
            raise Exception(f"Field {ref_field} does not exist in {rel_model.__name__} "
                            f"for relation {model.__name__}.{relation_name}")

    model.__metadata__.relations[relation_name] = Relation(model, rel_model, join_on)


def db_name(val: str):
    return field(metadata={'db_name': val})
