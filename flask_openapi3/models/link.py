# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:45
from typing import Any, Optional

from pydantic import BaseModel

from .server import Server


class Link(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#link-object
    """

    operationRef: Optional[str] = None
    operationId: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None
    requestBody: Optional[Any] = None
    description: Optional[str] = None
    server: Optional[Server] = None

    model_config = {
        "extra": "allow"
    }
