# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:57
from typing import Optional

from pydantic import BaseModel, Field


class ServerVariable(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#server-variable-object
    """

    enum: Optional[list[str]] = Field(None, min_length=1)
    default: str
    description: Optional[str] = None

    model_config = {
        "extra": "allow"
    }
