# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:41
from typing import TYPE_CHECKING, Optional, Union

from pydantic import BaseModel

from .reference import Reference

if TYPE_CHECKING:  # pragma: no cover
    from .header import Header
else:
    Header = "Header"


class Encoding(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#encoding-object
    """

    contentType: Optional[str] = None
    headers: Optional[dict[str, Union[Header, Reference]]] = None
    style: Optional[str] = None
    explode: Optional[bool] = None
    allowReserved: bool = False

    model_config = {
        "extra": "allow"
    }
