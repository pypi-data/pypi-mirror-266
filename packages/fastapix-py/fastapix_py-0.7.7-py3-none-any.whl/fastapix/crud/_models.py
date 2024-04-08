# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : _models.py
# @Time     : 2023/10/29 15:45
from functools import cached_property
from typing import Type, Dict, Optional, Union, List, Iterable, Any, Tuple

from fastapi.utils import create_cloned_field, create_response_field
from pydantic import BaseModel
from sqlalchemy import select, Column
from sqlalchemy.orm import InstrumentedAttribute, RelationshipProperty
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import Label
from sqlmodel import SQLModel

from fastapix.common.pydantic import (
    PYDANTIC_V2, ModelField, FieldInfo,
    create_model_by_fields, model_fields
)

EMPTY_LIST: list = []


class ModelFieldProxy:
    """Proxy for pydantic ModelField to modify some attributes without affecting the original ModelField.
    Reduce the deep copy of the original ModelField to improve performance.
    """

    def __init__(self, modelfield: ModelField, update: Dict[str, Any] = None):
        self.__dict__["_modelfield"] = modelfield
        self.__dict__["_update"] = update or {}

    def __getattr__(self, item):
        if item == "cloned_field":
            return self.__dict__[item]
        return self.__dict__["_update"].get(item, getattr(self.__dict__["_modelfield"], item))

    def __setattr__(self, key, value):
        self.__dict__["_update"][key] = value

    def cloned_field(self):
        modelfield = create_cloned_field(self.__dict__["_modelfield"])
        if PYDANTIC_V2:
            kwargs = self.__dict__["_update"]
            name = kwargs.pop("name", modelfield.name)
            alias = kwargs.get("alias", None)
            if alias:
                kwargs.setdefault("validation_alias", alias)
                kwargs.setdefault("serialization_alias", alias)
            field_info = FieldInfo.merge_field_infos(modelfield.field_info, **kwargs)
            field_info.annotation = modelfield.field_info.annotation
            return ModelField(field_info=field_info, name=name, mode=modelfield.mode)
        for k, v in self.__dict__["_update"].items():
            setattr(modelfield, k, v)
        return modelfield


class SQLModelParser:
    def __init__(
            self,
            model: Type[SQLModel],
            read_extra_fields: List[Union[str, InstrumentedAttribute, Label, Any]] = EMPTY_LIST,
            create_extra_fields: List[Union[str, InstrumentedAttribute, Label, Any]] = EMPTY_LIST,
            update_extra_fields: List[Union[str, InstrumentedAttribute, Label, Any]] = EMPTY_LIST,
    ):
        self.Model = model
        assert self.Model, "model is None"
        assert hasattr(self.Model, "__table__"), "model must be has __table__ attribute."
        self.__table__ = self.Model.__table__  # type: ignore
        self.__fields__ = model_fields(self.Model)
        self.pk_name: str = self.__table__.primary_key.columns.keys()[0]
        self.pk: InstrumentedAttribute = self.Model.__dict__[self.pk_name]
        self.pk_modelfield: ModelField = self.__fields__[self.pk_name]
        fields = self.model_insfields
        self.fields = [sqlfield for sqlfield in self.filter_insfield(fields + [self.pk], save_class=(Label,))]
        assert self.fields, "fields is None"

        self.read_extra_fields = read_extra_fields
        self.create_extra_fields = create_extra_fields
        self.update_extra_fields = update_extra_fields

    @cached_property
    def model_insfields(self) -> List[Union[str, InstrumentedAttribute]]:
        return self.filter_insfield(self.Model.__dict__.values())

    @cached_property
    def _select_entities(self) -> Dict[str, Union[InstrumentedAttribute, Label]]:
        return {self.get_alias(insfield): insfield for insfield in self.fields + self.read_extra_fields}

    def get_select(self) -> Select:
        return select(*self._select_entities.values())

    def get_insfield(self, field: Union[str, InstrumentedAttribute]) -> Optional[InstrumentedAttribute]:
        if isinstance(field, str):
            field = self.Model.__dict__.get(field, None)
        if isinstance(field, InstrumentedAttribute):
            return field
        return None

    def get_alias(self, field: Union[Column, str, InstrumentedAttribute, Label]) -> str:
        if isinstance(field, Column):
            return field.name
        elif isinstance(field, InstrumentedAttribute):
            return field.key
        elif isinstance(field, Label):
            return field.key
        elif isinstance(field, str) and field in self.__fields__:
            return field
        return ""

    def filter_insfield(
            self,
            fields: Iterable[Union[str, InstrumentedAttribute, Label, Any]],
            save_class: Tuple[Union[type, Tuple[Any, ...]], ...] = None,
            exclude_property: Tuple[Union[type, Tuple[Any, ...]], ...] = (RelationshipProperty,),
    ) -> List[Union[InstrumentedAttribute, Any]]:
        result = []
        for field in fields:
            insfield = self.get_insfield(field)
            if insfield is not None:
                if isinstance(insfield.property, exclude_property):
                    continue
            elif save_class and isinstance(field, save_class):
                insfield = field
            if insfield is not None:
                result.append(insfield)
        return sorted(set(result), key=result.index)  # 去重复并保持原顺序

    def get_modelfield(
            self, field: Union[ModelField, str, InstrumentedAttribute, Label], clone: bool = False
    ) -> Optional[Union[ModelField, "ModelFieldProxy"]]:
        modelfield = None
        update = {}
        if isinstance(field, InstrumentedAttribute):
            modelfield = model_fields(field.class_).get(field.key, None)
            if not modelfield:  # Maybe it's a declared_attr or column_property.
                return None
            if field.class_.__table__ is not self.__table__:
                update = {
                    "name": field.key,
                    "alias": self.get_alias(field),
                }
        elif isinstance(field, str) and field in self.__fields__:
            modelfield = self.__fields__[field]
        elif isinstance(field, ModelField):
            modelfield = field
        elif isinstance(field, Label):
            modelfield = _get_label_modelfield(field)
        if not modelfield:
            return None
        field_proxy = ModelFieldProxy(modelfield, update=update)
        return field_proxy.cloned_field() if clone else field_proxy

    def filter_modelfield(
            self,
            fields: Iterable[Union[str, InstrumentedAttribute, Label, Any]],
            save_class: Tuple[Union[type, Tuple[Any, ...]], ...] = (ModelField,),
            exclude: Iterable[str] = None,
    ) -> List[ModelField]:
        exclude = exclude or []
        # Filter out any non-model fields from the read fields
        fields = self.filter_insfield(fields, save_class=save_class)
        modelfields = [self.get_modelfield(ins, clone=True) for ins in fields]
        # Filter out any None values or out excluded fields
        modelfields = [field for field in modelfields if field and field.name not in exclude]
        return modelfields

    def create_schema_read(self) -> Type[BaseModel]:
        fields = self._select_entities.values()
        exclude = {
            name
            for name, field in model_fields(self.Model).items()
            if not getattr(field.field_info, 'read', False)
        }
        modelfields = self.filter_modelfield(
            fields,
            save_class=(
                Label,
                ModelField,
            ),
            exclude=exclude
        )
        return create_model_by_fields(
            name=f"{self.Model.__name__}Read",
            fields=modelfields,
            orm_mode=True,
            extra="allow",
            mode="read",
            __config__=self.Model.model_config if PYDANTIC_V2 else self.Model.Config
        )

    def create_schema_update(self) -> Type[BaseModel]:
        exclude = {
            name
            for name, field in model_fields(self.Model).items()
            if not getattr(field.field_info, 'update', False)
        }
        modelfields = self.filter_modelfield(self.fields + self.create_extra_fields, exclude=exclude)
        return create_model_by_fields(
            name=f"{self.Model.__name__}Update",
            fields=modelfields,
            set_none=True,
            __config__=self.Model.model_config if PYDANTIC_V2 else self.Model.Config
        )

    def create_schema_create(self) -> Type[BaseModel]:
        exclude = {
            name
            for name, field in model_fields(self.Model).items()
            if not getattr(field.field_info, 'create', False)
        }
        modelfields = self.filter_modelfield(self.fields + self.update_extra_fields, exclude=exclude)
        return create_model_by_fields(
            name=f"{self.Model.__name__}Create",
            fields=modelfields,
            __config__=self.Model.model_config if PYDANTIC_V2 else self.Model.Config
        )


def _get_label_modelfield(label: Label) -> ModelField:
    modelfield = getattr(label, "__ModelField__", None)
    if modelfield is None:
        try:
            type_ = label.expression.type.python_type
        except NotImplementedError:
            type_ = str
        modelfield = create_response_field(
            name=label.key,
            type_=type_,
        )
        label.__ModelField__ = modelfield
    return modelfield


def LabelField(label: Label, field: FieldInfo, type_: type = str) -> Label:
    """Use for adding FieldInfo to sqlalchemy Label type"""
    modelfield = _get_label_modelfield(label)
    field.alias = label.key
    if PYDANTIC_V2:
        field.annotation = type_
    modelfield.field_info = field
    label.__ModelField__ = modelfield
    return label
