# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:36
from typing import Optional, Union, Any

from pydantic import BaseModel, Field

from .callback import Callback
from .example import Example
from .header import Header
from .link import Link
from .parameter import Parameter
from .path_item import PathItem
from .reference import Reference
from .request_body import RequestBody
from .response import Response
from .schema import Schema
from .security_scheme import SecurityScheme


class Components(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#components-object
    """

    schemas: Optional[dict[str, Union[Reference, Schema]]] = Field(None)
    responses: Optional[dict[str, Union[Response, Reference]]] = None
    parameters: Optional[dict[str, Union[Parameter, Reference]]] = None
    examples: Optional[dict[str, Union[Example, Reference]]] = None
    requestBodies: Optional[dict[str, Union[RequestBody, Reference]]] = None
    headers: Optional[dict[str, Union[Header, Reference]]] = None
    securitySchemes: Optional[dict[str, Union[SecurityScheme, dict[str, Any]]]] = None
    links: Optional[dict[str, Union[Link, Reference]]] = None
    callbacks: Optional[dict[str, Union[Callback, Reference]]] = None
    pathItems: Optional[dict[str, Union[PathItem, Reference]]] = None

    model_config = {
        "extra": "allow"
    }
