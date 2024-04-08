from typing import TypedDict, Callable, Sequence
import sys
import asyncio
import csv
from io import StringIO
import decimal
from enum import Enum
from datetime import date, datetime
from urllib.request import urlopen

from ariadne import SubscriptionType
from asyncpg import Connection
from graphql import GraphQLError, GraphQLResolveInfo, GraphQLObjectType, GraphQLEnumType, get_named_type
from pyparsing import ParseException
import pypika
from pypika import functions as func
from pypika.queries import QueryBuilder

from . import models_functions as f
from . import pypika_extentions as func2
from .database import LockedDB
from .filter_parser import number_filter_parser, date_filter_parser, datetime_filter_parser, boolean_filter_parser
from .graphql_app import check_permission, HideResult
from .models_utils import BaseModel, ValueEnum, T
from .request_utils import get_db


class FieldFilter(TypedDict):
    field_name: str
    value: str


class FileUpload(TypedDict):
    data_url: str | None
    filename: str


def data_url_to_bytes(file: FileUpload) -> bytes:
    with urlopen(file['data_url']) as response:
        return response.read()


def get_csv_line_reader(file_upload: FileUpload):
    file = StringIO(data_url_to_bytes(file_upload).decode('utf-8'))
    return csv.reader(file)


def get_csv_dict_reader(file_upload: FileUpload) -> csv.DictReader:
    file = StringIO(data_url_to_bytes(file_upload).decode('utf-8'))
    return csv.DictReader(file)


class PyodbcParams:
    def __init__(self):
        self.params = []

    def add(self, value):
        self.params.append(value)
        return pypika.Parameter('?')


# Resolver Tools

async def get_or_gql_error(db: Connection | LockedDB, model: type[T], primary_keys: Sequence) -> T:
    """ Primary keys need to be real values """
    row = await f.get(db, model, primary_keys)
    if row is None:
        raise GraphQLError(f"Could not get {model.__name__} with keys {','.join(primary_keys)}")
    return row


def separate_filters(filters: list[FieldFilter], field_names_to_separate: list[str]):
    """ When some filters are automatically handled, and others you need to write custom SQLAlchemy queries """
    newfilters = []
    separated = []
    for filt in filters:
        if filt['field_name'] in field_names_to_separate:
            separated.append(filt)
        else:
            newfilters.append(filt)
    return newfilters, separated


# Complete Resolvers

def resolve_type_inspector_factory(model_list: list[BaseModel]):
    models_dict = {model.__name__: model for model in model_list}

    def resolve_type_inspector(_, info: GraphQLResolveInfo, type_name: str):
        gqltype = info.schema.get_type(type_name)
        if gqltype is None or not isinstance(gqltype, GraphQLObjectType):
            return None

        # Primary Keys. Raise error when using directive and model not found, else ignore
        model_name = getattr(gqltype, '__modelname__', type_name)
        model: type[BaseModel] | None = models_dict.get(model_name)
        if model is not None:
            primary_keys = model.__metadata__.primary_keys
        elif hasattr(gqltype, '__modelname__'):
            raise GraphQLError(f"Could not find model with name {model_name}")
        else:
            primary_keys = None

        all_filter = hasattr(gqltype, '__all_filter__')
        field_details = []
        for field_name, field in gqltype.fields.items():
            caption = getattr(field, '__caption__', field_name.title().replace('_', ' '))
            dataclass_field = model.__metadata__.dataclass_fields.get(field_name) if model is not None else None
            is_database = dataclass_field is not None
            field_filter_type = None
            if getattr(field, '__filter__', is_database or all_filter):  # If has filter
                if is_database:
                    field_type = f.extract_main_type(dataclass_field.type)
                    if field_type is str or issubclass(field_type, ValueEnum) or issubclass(field_type, Enum):
                        field_filter_type = 'STRING'
                    elif field_type in [int, float, decimal.Decimal]:
                        field_filter_type = 'NUMBER'
                    elif field_type is date:
                        field_filter_type = 'DATE'
                    elif field_type is datetime:
                        field_filter_type = 'DATE'
                    elif field_type is bool:
                        field_filter_type = 'BOOLEAN'
                    else:
                        raise GraphQLError(f"Cannot filter on column type {field_type}")
                else:  # Deducing filter type from GraphQL type
                    field_type = get_named_type(field.type)
                    if field_type is None:
                        raise Exception('Can only filter on Named Types')

                    if field_type.name == 'String':
                        field_filter_type = 'STRING'
                    elif field_type.name in ['Int', 'Float']:
                        field_filter_type = 'NUMBER'
                    elif field_type.name in ['Date', 'DateTime']:
                        field_filter_type = 'DATE'
                    elif field_type.name == 'Boolean':
                        field_filter_type = 'BOOLEAN'
                    elif isinstance(field_type, GraphQLEnumType):
                        field_filter_type = 'STRING'  # Consider Enum as strings
                    else:
                        raise GraphQLError(f'Type {field_type.name} cannot support filtering on field {field_name}')

            field_details.append({
                'field_name': field_name,
                'caption': caption,
                'is_database': is_database,
                'filter_type': field_filter_type,
                'editable': False  # Todo: implement
            })

        return {'field_details': field_details, 'primary_keys': primary_keys}
    return resolve_type_inspector


def apply_filter_to_query(q: QueryBuilder, field: pypika.Field, field_type, value) -> QueryBuilder:
    try:
        if field_type is str or issubclass(field_type, ValueEnum) or issubclass(field_type, Enum):
            # cast used to make Enum behave like strings.
            return q.where(func.Lower(func.Cast(field, 'varchar')).like(value.lower()))
        elif field_type in [int, float, decimal.Decimal]:
            return number_filter_parser(q, field, value)
        elif field_type is date:
            return date_filter_parser(q, field, value)
        elif field_type is datetime:
            return datetime_filter_parser(q, field, value)
        elif field_type is bool:
            return boolean_filter_parser(q, field, value)
        raise GraphQLError(f"Cannot filter on column type {field_type}")
    except ParseException as e:
        raise GraphQLError(f"Cannot parse value: {value} for field {field} of type {field_type} [{e}]")


def load_from_model_query(
        model: type[BaseModel], filters: list[FieldFilter], limit: int | None, offset: int | None,
        query_modifier: Callable[[QueryBuilder], QueryBuilder] | None = None, init_query: QueryBuilder | None = None
) -> QueryBuilder:
    query_class = model.__metadata__.registry.query_class

    q = query_class.from_(f.t(model)).select(*f.fs(model)) if init_query is None else init_query

    for filt in filters:
        full_name = filt['field_name']
        value = filt['value']

        *relation_names, field_name = full_name.split('.')
        current_model = model
        for relation_name in relation_names:
            # Join relationship, then get relation model
            q = f.join_relation(q, current_model, relation_name)
            current_model = f.get_relation_model(current_model, relation_name)

        # Deducing filter type by model column type. Contrary to resolve_type_inspector.
        field: pypika.Field = getattr(current_model, field_name)
        field_type = f.get_field_main_type(current_model, field_name)

        if f.is_field_list_type(current_model, field_name):  # Handle lists
            unnested_field_name = field_name + '_unnested'
            unnested_field = pypika.Field(unnested_field_name)
            q = q.where(func2.Exists(
                apply_filter_to_query(
                    query_class.from_(func2.Unnest(field).as_(unnested_field_name)).select('*'),
                    unnested_field, field_type, value
                )
            ))
        else:
            q = apply_filter_to_query(q, field, field_type, value)

    if query_modifier is not None:
        q = query_modifier(q)

    return q.limit(limit).offset(offset)


def resolve_type_loader_factory(model_list: list[type[BaseModel]]):
    models_dict = {model.__name__: model for model in model_list}

    async def resolve_type_loader(_, info, type_name: str, filters: list[FieldFilter], limit: int, offset: int):
        gqltype = info.schema.get_type(type_name)
        if gqltype is None:  # Check if Type exists in GQL
            raise GraphQLError(f'Type {type_name} does not exist')
        model_name = getattr(gqltype, '__modelname__', type_name)

        try:
            model = models_dict[model_name]
        except KeyError:
            raise GraphQLError(f"Could not find {model_name} in Models")

        registry = model.__metadata__.registry

        q = load_from_model_query(model, filters, limit, offset).orderby(
            *(model.__metadata__.database_fields[pkname] for pkname in model.__metadata__.primary_keys)
        )

        if registry.custom_loader is None:
            recs = await get_db(info).fetch(q)
        else:
            recs = await registry.custom_loader(info, q)

        objs = f.build_all(model, recs)
        for obj in objs:
            obj.__typename = type_name
        return objs

    return resolve_type_loader


def simple_table_resolver_factory(model: type[T], query_modifiers: Callable[[QueryBuilder], QueryBuilder] | None = None):
    async def simple_table_resolver(_, info, filters: list[FieldFilter], limit: int, offset: int) -> list[T]:
        q = load_from_model_query(model, filters, limit, offset, query_modifiers)
        if model.__metadata__.registry.custom_loader is None:
            recs = await get_db(info).fetch(q)
        else:
            recs = await model.__metadata__.registry.custom_loader(info, q)
        return f.build_all(model, recs)
    return simple_table_resolver


# Subscription tools

def subscription_permission_check(generator):
    async def new_generator(obj, info, *args, **kwargs):
        try:
            check_permission(info)
        except HideResult:
            yield None
            return

        async for res in generator(obj, info, *args, **kwargs):
            yield res

    return new_generator


def assign_simple_resolver(sub_object: SubscriptionType):
    def simple_resolver(val, *_, **__):
        return val

    for sub_field_name in sub_object._subscribers:
        if sub_field_name not in sub_object._resolvers:
            sub_object.set_field(sub_field_name, simple_resolver)


# External executors

async def external_module_executor(module_name, *args: str):
    proc = await asyncio.create_subprocess_exec(sys.executable, '-u', '-m', f'scripts.{module_name}', *args,
                                                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    while not proc.stdout.at_eof():
        data = await proc.stdout.readline()
        yield data.decode().rstrip()

    error = await proc.stderr.read()
    if error:
        raise GraphQLError(error.decode().rstrip())


async def external_script_executor(script_name, *args: str):
    proc = await asyncio.create_subprocess_exec(script_name, *args,
                                                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    while not proc.stdout.at_eof():
        data = await proc.stdout.readline()
        yield data.decode().rstrip()

    error = await proc.stderr.read()
    if error:
        raise GraphQLError(error.decode().rstrip())
