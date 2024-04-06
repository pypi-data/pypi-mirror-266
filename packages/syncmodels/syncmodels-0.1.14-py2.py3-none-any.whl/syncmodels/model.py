"""This module contains the base model support.
"""

import sys
import inspect
import re

from typing import List, Optional, Union, Any
from datetime import datetime
from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BaseModel, PlainSerializer, BeforeValidator
from dateutil.parser import parse


# ----------------------------------------------------------
# Hide library elements to be used as base
# ----------------------------------------------------------
from enum import Enum as _Enum
from enum import IntEnum as _IntEnum
from enum import Flag as _Flag
from pydantic import BaseModel as _BaseModel

# ----------------------------------------------------------
# Pydantic classes
# ----------------------------------------------------------
from pydantic import Field
from pydantic.dataclasses import dataclass
from pydantic.functional_validators import field_validator

# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------
from agptools.helpers import new_uid, DATE
from syncmodels.helpers.faker import fake

# pydantic custom datetime
Datetime = Annotated[
    datetime,
    BeforeValidator(lambda x: DATE(x)),
    PlainSerializer(lambda x: x.strftime("%Y-%m-%dT%H:%M:%SZ")),
]


class SyncConfig:
    # anystr_lower = True
    allow_population_by_field_name = True
    arbitrary_types_allowed = True

    # min_anystr_length = 2
    # max_anystr_length = 10
    ## validate_all = True
    ## validate_assignment = True
    # error_msg_templates = {
    #'value_error.any_str.max_length': 'max_length:{limit_value}',
    # }
    # smart_union = True
    pass


# ==========================================================
# Own implementation of Enums
# ==========================================================
class BaseInterface:

    @classmethod
    def _klass_fqname(cls):
        return f"{cls.__module__}.{cls.__name__}"

    @classmethod
    def _klass_fqtable(cls):
        return cls._klass_fqname().replace(".", "_")

    @classmethod
    def _fqtable2fqname(cls, fqtable):
        return fqtable.replace("_", ".")

    @classmethod
    def _build_meta(cls):
        pass

    @classmethod
    def _locate_classes(cls):
        for name, module in list(sys.modules.items()):
            # SKIP some modules that will modify module itself or create any error
            if re.match(r"(pydantic\.)", name):
                print(f"- inspecting: {name}")
                continue
            print(f"+ inspecting: {name}")
            for fqname in list(dir(module)):
                # print(f"      : {fqname}")
                item = getattr(module, fqname)
                if inspect.isclass(item):
                    if issubclass(
                        item,
                        (BaseInterface,),
                    ):
                        fqname = item._klass_fqname()
                        if fqname not in META:
                            meta = item._build_meta()
                            # add both keys for faster access
                            META[fqname] = meta
                            META[item._klass_fqtable()] = meta


class EnumInterface(BaseInterface):

    @classmethod
    def _build_meta(cls):
        try:
            meta = cls._member_map_
        except AttributeError:
            meta = {}

        return {
            "klass": cls,
            "meta": meta,
        }


class Enum(EnumInterface, _Enum):
    pass


class Flag(EnumInterface, _Flag):
    pass


class IntEnum(EnumInterface, _IntEnum):
    pass


# ==========================================================
# Own implementation of BaseModel
# ==========================================================
# @dataclass(config=SyncConfig)
META = {}


def nop(schema, meta, *args, **kw):
    pass


def pyd_analyze(schema, meta, *args, **kw):
    schema2 = schema["schema"]
    type_ = schema2["type"]
    result = PYD_HOOK[type_](schema2, meta, *args, **kw)
    return result


def pyd_analyze_same(schema, meta, *args, **kw):
    type_ = schema["type"]
    result = PYD_HOOK[type_](schema, meta, *args, **kw)
    return result


def pyd_dict(schema, meta, *args, **kw):
    result = {}
    for key in "keys", "values":
        key2 = f"{key}_schema"
        result = PYD_HOOK[key2](schema[key2], meta, *args, **kw)
        if result:
            result[key] = result
    return result


def pyd_definitions(schema, meta, *args, **kw):
    for sch in schema["definitions"]:
        type_ = sch["type"]
        PYD_HOOK[type_](sch, meta, *args, **kw)


def pyd_definition_ref(schema, meta, *args, **kw):
    foo = 1
    # klass = schema['cls']
    # assert issubclass(klass, BaseModel)
    # assert schema['type'] in ('model',)
    # schema2 = schema['schema']
    # type_ = schema2['type']
    # assert type_ in ('model-fields',)

    # for id_key in ('id',):
    # if id_key in schema2['fields']:
    # return id_key


def pyd_list(schema, meta, *args, **kw):
    result = {}
    sch = schema["items_schema"]
    type_ = sch["type"]
    PYD_HOOK[type_](sch, meta, *args, **kw)
    return result


def pyd_model(schema, meta, *args, **kw):
    # klass = schema['cls']
    # assert issubclass(klass, BaseModel)
    assert schema["type"] in ("model",)
    schema2 = schema["schema"]
    type_ = schema2["type"]
    assert type_ in ("model-fields",)
    PYD_HOOK[type_](schema2, meta, *args, **kw)

    # for id_key in ('id',):
    # if id_key in schema2['fields']:
    # return id_key

    # raise RuntimeError(f"Review pyd_model using: {name} : {schema}")


def pyd_model_fields(schema, meta, *args, **kw):
    for name, field in schema["fields"].items():
        if re.match(r"id", name):
            result = True
        else:
            field_schema = field["schema"]
            print(f"{name}: {field_schema}")
            type_1 = field_schema["type"]
            result = PYD_HOOK[type_1](field_schema, meta)
        if result:
            meta[name] = result


def pyd_lax_or_strict(schema, meta, *args, **kw):
    klass = schema["cls"]
    assert issubclass(klass, BaseModel)
    assert schema["type"] in ("model",)
    schema2 = schema["schema"]
    type_ = schema2["type"]
    assert type_ in ("model-fields",)

    for id_key in ("id",):
        if id_key in schema2["fields"]:
            return id_key


PYD_HOOK = {
    "default": pyd_analyze,
    "definitions": pyd_definitions,
    "definition-ref": pyd_definition_ref,
    "dict": pyd_dict,
    "int": nop,
    "keys_schema": pyd_analyze_same,
    "float": nop,
    "function-after": nop,
    "lax-or-strict": nop,
    "list": pyd_list,
    "model-fields": pyd_model_fields,
    "model": pyd_model,
    "nullable": pyd_analyze,
    "str": nop,
    "values_schema": pyd_analyze_same,
}


class BaseModel(BaseInterface, _BaseModel):

    _fquid: Optional[str] = ""
    _uid: Optional[str] = ""

    @classmethod
    def _get_meta(cls, fqid=None):
        if fqid:
            fqname = fqid.split(":")[0]
        else:
            fqname = cls._klass_fqname()

        meta = META.get(fqname)
        if not meta:
            cls._locate_classes()
        meta = META.get(fqname)
        return meta

    @classmethod
    def _build_meta(cls):
        if "Project" in str(cls):
            foo = 1
        meta = {}
        core_schema = cls.__pydantic_core_schema__

        # def func(schema_1):
        # if schema_1['type'] in ('model',):
        # schema_1 = schema_1['schema']
        # assert schema_1['type'] in ('model-fields',)
        # for name, field in schema_1['fields'].items():
        # field_schema = field['schema']
        # print(f"{name}: {field_schema}")
        # type_1 = field_schema['type']
        # result = PYD_HOOK[type_1](name, field_schema)
        # if result:
        # meta[name] = result
        # foo = 1

        # schema = core_schema['schema']
        type_ = core_schema["type"]
        assert type_ in (
            "model",
            "definitions",
        )
        PYD_HOOK[type_](core_schema, meta)

        return {
            "klass": cls,
            "meta": meta,
        }

    @classmethod
    def _new_uid(cls):
        table = cls._klass_fqtable()
        return f"{table}:{new_uid()}"

    @classmethod
    def _random_data_(cls):
        return {
            "name": fake.item_name(),
            # "name": fake.name(),
            # "description": fake.sentence(),
            "description": fake.paragraph(nb_sentences=1),
            "id": cls._new_uid(),
        }

    @classmethod
    def random_item(cls):
        data = {
            **cls._random_data_(),
            "foo": 1,
        }
        return cls(**data)

    def __init__(self, /, **data: Any) -> None:  # type: ignore
        uid = data.pop("id", None)
        if not uid:
            uid = new_uid()
            if ":" not in uid:
                table = self._klass_fqtable()
                uid = f"{table}:{uid}"
        super().__init__(id=uid, **data)
