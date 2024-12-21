# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:46
from typing import Any, Optional, Union

from pydantic import BaseModel, Field

from .encoding import Encoding
from .example import Example
from .reference import Reference
from .schema import Schema


class MediaType(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#media-type-object
    """

    media_type_schema: Optional[Union[Reference, Schema]] = Field(default=None, alias="schema")
    example: Optional[Any] = None
    examples: Optional[dict[str, Union[Example, Reference]]] = None
    encoding: Optional[dict[str, Encoding]] = None

    model_config = {
        "extra": "allow"
    }
