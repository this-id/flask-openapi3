# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/10/14 16:09
import typing
from typing import Optional, List, Dict, Any, Callable

from .models import ExternalDocumentation
from .models import Server
from .models import Tag
from .types import ResponseDict
from .utils import HTTPMethod
from .utils import convert_responses_key_to_string
from .utils import get_operation
from .utils import get_operation_id_for_path
from .utils import get_responses
from .utils import parse_and_store_tags
from .utils import parse_method
from .utils import parse_parameters
from .utils import parse_rule

if typing.TYPE_CHECKING:  # pragma: no cover
    from .openapi import OpenAPI


class APIView:
    def __init__(
            self,
            url_prefix: Optional[str] = None,
            view_tags: Optional[List[Tag]] = None,
            view_security: Optional[List[Dict[str, List[str]]]] = None,
            view_responses: Optional[ResponseDict] = None,
            doc_ui: bool = True,
            operation_id_callback: Callable = get_operation_id_for_path,
    ):
        """
        Create a class-based view

        Args:
            url_prefix: A path to prepend to all the APIView's urls
            view_tags: APIView tags for every API.
            view_security: APIView security for every API.
            view_responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Enable OpenAPI document UI (Swagger UI and Redoc). Defaults to True.
            operation_id_callback: Callback function for custom operation_id generation.
                                   Receives name (str), path (str) and method (str) parameters.
                                   Defaults to `get_operation_id_for_path` from utils
        """
        self.url_prefix = url_prefix
        self.view_tags = view_tags or []
        self.view_security = view_security or []

        # Convert key to string
        self.view_responses = convert_responses_key_to_string(view_responses or {})

        self.doc_ui = doc_ui
        self.operation_id_callback: Callable = operation_id_callback

        self.views: Dict = dict()
        self.paths: Dict = dict()
        self.components_schemas: Dict = dict()
        self.tags: List[Tag] = []
        self.tag_names: List[str] = []

    def route(self, rule: str):
        """Decorator for view class"""

        def wrapper(cls):
            if self.views.get(rule):  # pragma: no cover
                raise ValueError(f"malformed url rule: {rule!r}")
            methods = []

            # Parse rule: merge url_prefix and format rule from /pet/<petId> to /pet/{petId}
            uri = parse_rule(rule, url_prefix=self.url_prefix)

            for method in HTTPMethod:
                cls_method = getattr(cls, method.lower(), None)
                if not cls_method:
                    continue
                methods.append(method)
                if self.doc_ui is False:
                    continue
                if not getattr(cls_method, "operation", None):
                    continue
                # Parse method
                parse_method(uri, method, self.paths, cls_method.operation)
                # Update operation_id
                if not cls_method.operation.operationId:
                    cls_method.operation.operationId = self.operation_id_callback(
                        name=cls_method.__qualname__,
                        path=rule,
                        method=method
                    )

            # Convert route parameters from {param} to <param>
            _rule = uri.replace("{", "<").replace("}", ">")
            self.views[_rule] = (cls, methods)

            return cls

        return wrapper

    def doc(
            self,
            *,
            tags: Optional[List[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            doc_ui: bool = True
    ) -> Callable:
        """
        Decorator for view method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        new_responses = convert_responses_key_to_string(responses or {})
        security = security or []
        tags = tags + self.view_tags if tags else self.view_tags

        def decorator(func):
            if self.doc_ui is False or doc_ui is False:
                return func

            # Global response combines API responses
            combine_responses = {**self.view_responses, **new_responses}

            # Create operation
            operation = get_operation(
                func,
                summary=summary,
                description=description,
                openapi_extensions=openapi_extensions
            )

            # Set external docs
            if external_docs:
                operation.externalDocs = external_docs

            # Unique string used to identify the operation.
            if operation_id:
                operation.operationId = operation_id

            # Only set `deprecated` if True, otherwise leave it as None
            if deprecated is not None:
                operation.deprecated = deprecated

            # Add security
            _security = (security or []) + self.view_security or None
            if _security:
                operation.security = _security

            # Add servers
            if servers:
                operation.servers = servers

            # Store tags
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)

            # Parse parameters
            parse_parameters(
                func,
                components_schemas=self.components_schemas,
                operation=operation
            )

            # Parse response
            get_responses(combine_responses, self.components_schemas, operation)
            func.operation = operation

            return func

        return decorator

    def register(
            self,
            app: "OpenAPI",
            url_prefix: Optional[str] = None,
            view_kwargs: Optional[Dict[Any, Any]] = None
    ) -> None:
        """
        Register the API views with the given OpenAPI app.

        Args:
            app: An instance of the OpenAPI app.
            url_prefix: A path to prepend to all the APIView's urls
            view_kwargs: Additional keyword arguments to pass to the API views.
        """
        for rule, (cls, methods) in self.views.items():
            for method in methods:
                func = getattr(cls, method.lower())
                header, cookie, path, query, form, body, raw = parse_parameters(func, doc_ui=False)
                view_func = app.create_view_func(
                    func,
                    header,
                    cookie,
                    path,
                    query,
                    form,
                    body,
                    raw,
                    view_class=cls,
                    view_kwargs=view_kwargs
                )

                if url_prefix and self.url_prefix and url_prefix != self.url_prefix:
                    rule = url_prefix + rule.removeprefix(self.url_prefix)
                elif url_prefix and not self.url_prefix:
                    rule = url_prefix.rstrip("/") + "/" + rule.lstrip("/")

                options = {
                    "endpoint": cls.__name__ + "." + method.lower(),
                    "methods": [method.upper()]
                }
                app.add_url_rule(rule, view_func=view_func, **options)
