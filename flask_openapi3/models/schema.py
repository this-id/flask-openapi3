# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:55
from typing import Any, Optional, Union

from pydantic import BaseModel, Field

from .data_type import DataType
from .discriminator import Discriminator
from .external_documentation import ExternalDocumentation
from .reference import Reference
from .xml import XML


class Schema(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#schema-object
    """
    ref: Optional[str] = Field(alias="$ref", default=None)
    title: Optional[str] = None
    multipleOf: Optional[float] = Field(default=None, gt=0.0)
    maximum: Optional[float] = None
    exclusiveMaximum: Optional[float] = None
    minimum: Optional[float] = None
    exclusiveMinimum: Optional[float] = None
    maxLength: Optional[int] = Field(default=None, ge=0)
    minLength: Optional[int] = Field(default=None, ge=0)
    pattern: Optional[str] = None
    maxItems: Optional[int] = Field(default=None, ge=0)
    minItems: Optional[int] = Field(default=None, ge=0)
    uniqueItems: Optional[bool] = None
    maxProperties: Optional[int] = Field(default=None, ge=0)
    minProperties: Optional[int] = Field(default=None, ge=0)
    required: Optional[list[str]] = Field(default=None)
    enum: Union[None, list[Any]] = Field(default=None)
    type: Optional[DataType] = Field(default=None)
    allOf: Optional[list[Union[Reference, "Schema"]]] = None
    oneOf: Optional[list[Union[Reference, "Schema"]]] = None
    anyOf: Optional[list[Union[Reference, "Schema"]]] = None
    schema_not: Optional[Union[Reference, "Schema"]] = Field(default=None, alias="not")
    items: Optional[Union[Reference, "Schema"]] = None
    properties: Optional[dict[str, Union[Reference, "Schema"]]] = None
    prefixItems: Optional[list[Union[Reference, "Schema"]]] = None
    additionalProperties: Optional[Union[bool, Reference, "Schema"]] = None
    description: Optional[str] = None
    schema_format: Optional[str] = Field(default=None, alias="format")
    default: Optional[Any] = None
    nullable: Optional[bool] = None
    discriminator: Optional[Discriminator] = None
    readOnly: Optional[bool] = None
    writeOnly: Optional[bool] = None
    xml: Optional[XML] = None
    externalDocs: Optional[ExternalDocumentation] = None
    example: Optional[Any] = None
    deprecated: Optional[bool] = None
