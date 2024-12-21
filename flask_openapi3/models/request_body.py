# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:53
from typing import Optional

from pydantic import BaseModel

from .media_type import MediaType


class RequestBody(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#request-body-object
    """

    description: Optional[str] = None
    content: dict[str, MediaType]
    required: Optional[bool] = True

    model_config = {
        "extra": "allow"
    }
