# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:52
from .path_item import PathItem

"""
https://spec.openapis.org/oas/v3.1.0#paths-object
"""
Paths = dict[str, PathItem]
