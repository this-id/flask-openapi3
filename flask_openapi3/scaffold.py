# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/8/30 9:40
import inspect
from functools import wraps
from typing import Callable, Optional, Any

from flask.wrappers import Response as FlaskResponse

from .models import ExternalDocumentation
from .models import Server
from .models import Tag
from .request import _validate_request
from .types import ParametersTuple
from .types import ResponseDict
from .utils import HTTPMethod


class APIScaffold:
    def _collect_openapi_info(
            self,
            rule: str,
            func: Callable,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            method: str = HTTPMethod.GET
    ) -> ParametersTuple:
        raise NotImplementedError   # pragma: no cover

    def register_api(self, api) -> None:
        raise NotImplementedError   # pragma: no cover

    def _add_url_rule(
            self,
            rule,
            endpoint=None,
            view_func=None,
            provide_automatic_options=None,
            **options,
    ) -> None:
        raise NotImplementedError   # pragma: no cover

    @staticmethod
    def create_view_func(
            func,
            header,
            cookie,
            path,
            query,
            form,
            body,
            raw,
            view_class=None,
            view_kwargs=None
    ):
        is_coroutine_function = inspect.iscoroutinefunction(func)
        if is_coroutine_function:
            @wraps(func)
            async def view_func(**kwargs) -> FlaskResponse:
                func_kwargs = _validate_request(
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    raw=raw,
                    path_kwargs=kwargs
                )

                # handle async request
                if view_class:
                    signature = inspect.signature(view_class.__init__)
                    parameters = signature.parameters
                    if parameters.get("view_kwargs"):
                        view_object = view_class(view_kwargs=view_kwargs)
                    else:
                        view_object = view_class()
                    response = await func(view_object, **func_kwargs)
                else:
                    response = await func(**func_kwargs)
                return response
        else:
            @wraps(func)
            def view_func(**kwargs) -> FlaskResponse:
                func_kwargs = _validate_request(
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    raw=raw,
                    path_kwargs=kwargs
                )

                # handle request
                if view_class:
                    signature = inspect.signature(view_class.__init__)
                    parameters = signature.parameters
                    if parameters.get("view_kwargs"):
                        view_object = view_class(view_kwargs=view_kwargs)
                    else:
                        view_object = view_class()
                    response = func(view_object, **func_kwargs)
                else:
                    response = func(**func_kwargs)
                return response

        if not hasattr(func, "view"):
            func.view = view_func

        return func.view

    def get(
            self,
            rule: str,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP GET method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
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

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, raw = \
                self._collect_openapi_info(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    responses=responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    openapi_extensions=openapi_extensions,
                    doc_ui=doc_ui,
                    method=HTTPMethod.GET
                )

            view_func = self.create_view_func(func, header, cookie, path, query, form, body, raw)
            options.update({"methods": [HTTPMethod.GET]})
            self._add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def post(
            self,
            rule: str,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP POST method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
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

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, raw = \
                self._collect_openapi_info(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    responses=responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    openapi_extensions=openapi_extensions,
                    doc_ui=doc_ui,
                    method=HTTPMethod.POST
                )

            view_func = self.create_view_func(func, header, cookie, path, query, form, body, raw)
            options.update({"methods": [HTTPMethod.POST]})
            self._add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def put(
            self,
            rule: str,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP PUT method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
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

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, raw = \
                self._collect_openapi_info(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    responses=responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    openapi_extensions=openapi_extensions,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PUT
                )

            view_func = self.create_view_func(func, header, cookie, path, query, form, body, raw)
            options.update({"methods": [HTTPMethod.PUT]})
            self._add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def delete(
            self,
            rule: str,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP DELETE method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
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

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, raw = \
                self._collect_openapi_info(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    responses=responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    openapi_extensions=openapi_extensions,
                    doc_ui=doc_ui,
                    method=HTTPMethod.DELETE
                )

            view_func = self.create_view_func(func, header, cookie, path, query, form, body, raw)
            options.update({"methods": [HTTPMethod.DELETE]})
            self._add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def patch(
            self,
            rule: str,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP PATCH method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
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

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, raw = \
                self._collect_openapi_info(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    responses=responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    openapi_extensions=openapi_extensions,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PATCH
                )

            view_func = self.create_view_func(func, header, cookie, path, query, form, body, raw)
            options.update({"methods": [HTTPMethod.PATCH]})
            self._add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator
