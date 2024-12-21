# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 10:58
"""
OpenAPI v3.1.0 schema types, created according to the specification:
https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md

The type orders are according to the contents of the specification:
https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#table-of-contents
"""

from typing import Optional, Union

from flask import Request
from pydantic import BaseModel

from .callback import Callback
from .components import Components
from .contact import Contact
from .discriminator import Discriminator
from .encoding import Encoding
from .example import Example
from .external_documentation import ExternalDocumentation
from .file import FileStorage
from .header import Header
from .info import Info
from .license import License
from .link import Link
from .media_type import MediaType
from .oauth_flow import OAuthFlow
from .oauth_flows import OAuthFlows
from .operation import Operation
from .parameter import Parameter
from .parameter_in_type import ParameterInType
from .path_item import PathItem
from .paths import Paths
from .reference import Reference
from .request_body import RequestBody
from .response import Response
from .responses import Responses
from .schema import Schema
from .security_requirement import SecurityRequirement
from .security_scheme import SecurityScheme
from .server import Server
from .server_variable import ServerVariable
from .style_values import StyleValues
from .tag import Tag
from .validation_error import UnprocessableEntity
from .validation_error import ValidationErrorModel
from .xml import XML

OPENAPI3_REF_PREFIX = "#/components/schemas"
OPENAPI3_REF_TEMPLATE = OPENAPI3_REF_PREFIX + "/{model}"


class APISpec(BaseModel):
    """https://spec.openapis.org/oas/v3.1.0#openapi-object"""
    openapi: str
    info: Info
    servers: Optional[list[Server]] = None
    paths: Paths
    components: Optional[Components] = None
    security: Optional[list[SecurityRequirement]] = None
    tags: Optional[list[Tag]] = None
    externalDocs: Optional[ExternalDocumentation] = None
    webhooks: Optional[dict[str, Union[PathItem, Reference]]] = None

    model_config = {
        "extra": "allow"
    }


class OAuthConfig(BaseModel):
    """
    https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/oauth2.md#oauth-20-configuration
    """
    clientId: Optional[str] = None
    clientSecret: Optional[str] = None
    realm: Optional[str] = None
    appName: Optional[str] = None
    scopeSeparator: Optional[str] = None
    scopes: Optional[str] = None
    additionalQueryStringParams: Optional[dict[str, str]] = None
    useBasicAuthenticationWithAccessCodeGrant: Optional[bool] = False
    usePkceWithAuthorizationCodeGrant: Optional[bool] = False


class RawModel(Request):
    mimetypes: list[str] = ["application/json"]


Encoding.model_rebuild()
Operation.model_rebuild()
PathItem.model_rebuild()
