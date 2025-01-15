# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:25
import os
import re
import sys
from importlib import import_module
from typing import Optional, List, Dict, Union, Any, Type, Callable

from flask import Flask, Blueprint, render_template_string
from pydantic import BaseModel

if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:  # pragma: no cover
    from importlib_metadata import entry_points  # type: ignore

from .blueprint import APIBlueprint
from .commands import openapi_command
from .models import APISpec
from .models import Components
from .models import ExternalDocumentation
from .models import Info
from .models import OPENAPI3_REF_PREFIX
from .models import Schema
from .models import Server
from .models import Tag
from .models import ValidationErrorModel
from .scaffold import APIScaffold
from .templates import openapi_html_string
from .types import ParametersTuple
from .types import ResponseDict
from .types import SecuritySchemesDict
from .utils import HTTPMethod
from .utils import HTTP_STATUS
from .utils import convert_responses_key_to_string
from .utils import get_model_schema
from .utils import get_operation
from .utils import get_operation_id_for_path
from .utils import get_responses
from .utils import make_validation_error_response
from .utils import parse_and_store_tags
from .utils import parse_method
from .utils import parse_parameters
from .view import APIView


class OpenAPI(APIScaffold, Flask):
    def __init__(
            self,
            import_name: str,
            *,
            info: Optional[Info] = None,
            security_schemes: Optional[SecuritySchemesDict] = None,
            responses: Optional[ResponseDict] = None,
            servers: Optional[List[Server]] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id_callback: Callable = get_operation_id_for_path,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            validation_error_status: Union[str, int] = 422,
            validation_error_model: Type[BaseModel] = ValidationErrorModel,
            validation_error_callback: Callable = make_validation_error_response,
            doc_ui: bool = True,
            doc_prefix: str = "/openapi",
            doc_url: str = "/openapi.json",
            **kwargs: Any
    ) -> None:
        """
        OpenAPI class that provides REST API functionality along with Swagger UI and Redoc.

        Args:
            import_name: The import name for the Flask application.
            info: Information about the API (title, version, etc.).
                See https://spec.openapis.org/oas/v3.1.0#info-object.
            security_schemes: Security schemes for the API.
                See https://spec.openapis.org/oas/v3.1.0#security-scheme-object.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            servers: An array of Server objects providing connectivity information to a target server.
            external_docs: External documentation for the API.
                See: https://spec.openapis.org/oas/v3.1.0#external-documentation-object.
            operation_id_callback: Callback function for custom operation ID generation.
                Receives name (str), path (str), and method (str) parameters.
                Defaults to `get_operation_id_for_path` from utils.
            openapi_extensions: Extensions to the OpenAPI Schema.
                See https://spec.openapis.org/oas/v3.1.0#specification-extensions.
            validation_error_status:
                HTTP Status of the response given when a validation error is detected by pydantic.
                Defaults to 422.
            validation_error_model: Validation error response model for OpenAPI Specification.
            validation_error_callback: Validation error response callback, the return format corresponds to
                the validation_error_model.
            doc_ui: Enable OpenAPI document UI (Swagger UI and Redoc).
                Defaults to True.
            doc_prefix: URL prefix used for OpenAPI document and UI.
                Defaults to "/openapi".
            doc_url: URL for accessing the OpenAPI specification document in JSON format.
                Defaults to "/openapi.json".
            **kwargs: Additional kwargs to be passed to Flask.
        """
        super(OpenAPI, self).__init__(import_name, **kwargs)

        # Set OpenAPI version and API information
        self.openapi_version = "3.1.0"
        self.info = info or Info(title="OpenAPI", version="1.0.0")

        # Set security schemes, responses, paths and components
        self.security_schemes = security_schemes

        # Convert key to string
        self.responses = convert_responses_key_to_string(responses or {})

        # Initialize instance variables
        self.paths: Dict = dict()
        self.components_schemas: Dict = dict()
        self.components = Components()

        # Initialize lists for tags and tag names
        self.tags: List[Tag] = []
        self.tag_names: List[str] = []

        # Set URL prefixes and endpoints
        self.doc_prefix = doc_prefix
        self.doc_url = doc_url

        # Set servers and external documentation
        self.severs = servers
        self.external_docs = external_docs

        # Set the operation ID callback function
        self.operation_id_callback: Callable = operation_id_callback

        # Set OpenAPI extensions
        self.openapi_extensions = openapi_extensions or {}

        # Set HTTP Response of validation errors within OpenAPI
        self.validation_error_status = str(validation_error_status)
        self.validation_error_model = validation_error_model
        self.validation_error_callback = validation_error_callback

        # Initialize the OpenAPI documentation UI
        if doc_ui:
            self._init_doc()

        # Add the OpenAPI command
        self.cli.add_command(openapi_command)  # type: ignore

        # Initialize specification JSON
        self.spec_json: Dict = {}
        self.spec = APISpec(
            openapi=self.openapi_version,
            info=self.info,
            paths=self.paths
        )

    def _init_doc(self) -> None:
        """
        Provide Swagger UI, Redoc, and Rapidoc
        """
        _here = os.path.dirname(__file__)
        template_folder = os.path.join(_here, "templates")
        static_folder = os.path.join(template_folder, "static")

        # Create the blueprint for OpenAPI documentation
        blueprint = Blueprint(
            "openapi",
            __name__,
            url_prefix=self.doc_prefix,
            template_folder=template_folder,
            static_folder=static_folder
        )

        # Add the API documentation URL rule
        blueprint.add_url_rule(
            rule=self.doc_url,
            endpoint="doc_url",
            view_func=lambda: self.api_doc
        )

        ui_templates = []
        # Iterate over all entry points in the "flask_openapi3.plugins" group
        for entry_point in entry_points(group="flask_openapi3.plugins"):
            try:
                module_path = entry_point.value
                module_name, class_name = module_path.rsplit(".", 1)
                module = import_module(module_name)
                plugin_class = getattr(module, class_name)
                plugin_register = plugin_class.register
                plugin_name = plugin_class.name
                plugin_display_name = plugin_class.display_name
                bp = plugin_register(doc_url=self.doc_url.lstrip("/"))
                self.register_blueprint(bp, url_prefix=self.doc_prefix)
                ui_templates.append({"name": plugin_name, "display_name": plugin_display_name})
            except (ModuleNotFoundError, AttributeError):  # pragma: no cover
                import traceback
                print(f"Warning: plugin '{entry_point.value}' registration failed.")
                traceback.print_exc()

        # Add URL rule for the home page
        blueprint.add_url_rule(
            rule="/",
            endpoint="openapi",
            view_func=lambda: render_template_string(
                self.config.get("OPENAPI_HTML_STRING") or openapi_html_string,
                ui_templates=ui_templates
            )
        )

        # Register the blueprint with the Flask application
        self.register_blueprint(blueprint)

    @property
    def api_doc(self) -> Dict:
        """
        Generate the OpenAPI specification JSON.

        Returns:
            The OpenAPI specification JSON as a dictionary.

        """
        if self.spec_json:
            return self.spec_json

        self.generate_spec_json()

        return self.spec_json

    def generate_spec_json(self):
        self.spec.openapi = self.openapi_version
        self.spec.info = self.info
        self.spec.paths = self.paths

        if self.severs:
            self.spec.servers = self.severs

        if self.external_docs:
            self.spec.externalDocs = self.external_docs

        # Set tags
        if self.tags:
            self.spec.tags = self.tags

        # Add ValidationErrorModel to components schemas
        schema = get_model_schema(self.validation_error_model)
        self.components_schemas[self.validation_error_model.__name__] = Schema(**schema)

        # Parse definitions
        definitions = schema.get("$defs", {})
        for name, value in definitions.items():
            self.components_schemas[name] = Schema(**value)

        # Set components
        self.components.schemas = self.components_schemas
        self.components.securitySchemes = self.security_schemes
        self.spec.components = self.components

        # Convert spec to JSON
        self.spec_json = self.spec.model_dump(mode="json", by_alias=True, exclude_unset=True, warnings=False)

        # Update with OpenAPI extensions
        self.spec_json.update(**self.openapi_extensions)

        # Handle validation error response
        for rule, path_item in self.spec_json["paths"].items():
            for http_method, operation in path_item.items():
                if operation.get("parameters") is None and operation.get("requestBody") is None:
                    continue
                if not operation.get("responses"):
                    operation["responses"] = {}
                if operation["responses"].get(self.validation_error_status):
                    continue
                operation["responses"][self.validation_error_status] = {
                    "description": HTTP_STATUS[self.validation_error_status],
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "array",
                                "items": {"$ref": f"{OPENAPI3_REF_PREFIX}/{self.validation_error_model.__name__}"}
                            }
                        }
                    }
                }

    def register_api(self, api: APIBlueprint, **options: Any) -> None:
        """
        Register an APIBlueprint.

        Args:
            api: The APIBlueprint instance to register.

            options: Additional keyword arguments are passed to :class:`~flask.blueprints.BlueprintSetupState`.
            They can be accessed in :meth:`~flask.Blueprint.record` callbacks.
            url_prefix, Blueprint routes will be prefixed with this.
            subdomain, Blueprint routes will match on this subdomain.
            url_defaults, Blueprint routes will use these default values for view arguments.

        """
        for tag in api.tags:
            if tag.name not in self.tag_names:
                # Append tag to the list of tags
                self.tags.append(tag)

                # Append tag name to the list of tag names
                self.tag_names.append(tag.name)

        # Update paths with the APIBlueprint's paths
        url_prefix = options.get("url_prefix")
        if url_prefix and api.url_prefix and url_prefix != api.url_prefix:
            api.paths = {url_prefix + k.removeprefix(api.url_prefix): v for k, v in api.paths.items()}
        elif url_prefix and not api.url_prefix:
            api.paths = {url_prefix.rstrip("/") + "/" + k.lstrip("/"): v for k, v in api.paths.items()}
        self.paths.update(**api.paths)

        # Update component schemas with the APIBlueprint's component schemas
        self.components_schemas.update(**api.components_schemas)

        # Register the APIBlueprint with the current instance
        self.register_blueprint(api, **options)

    def register_api_view(
            self,
            api_view: APIView,
            url_prefix: Optional[str] = None,
            view_kwargs: Optional[Dict[Any, Any]] = None
    ) -> None:
        """
        Register APIView

        Args:
            api_view: The APIView instance to register.
            url_prefix: A path to prepend to all the APIView's urls
            view_kwargs: Additional keyword arguments to pass to the API views.
        """
        if view_kwargs is None:
            view_kwargs = {}

        # Iterate through tags of the APIView
        for tag in api_view.tags:
            if tag.name not in self.tag_names:
                # Append tag to the list of tags
                self.tags.append(tag)

                # Append tag name to the list of tag names
                self.tag_names.append(tag.name)

        # Update paths with the APIView's paths
        if url_prefix and api_view.url_prefix and url_prefix != api_view.url_prefix:
            api_view.paths = {url_prefix + k.removeprefix(api_view.url_prefix): v for k, v in api_view.paths.items()}
        elif url_prefix and not api_view.url_prefix:
            api_view.paths = {url_prefix.rstrip("/") + "/" + k.lstrip("/"): v for k, v in api_view.paths.items()}
        self.paths.update(**api_view.paths)

        # Update component schemas with the APIView's component schemas
        self.components_schemas.update(**api_view.components_schemas)

        # Register the APIView with the current instance
        api_view.register(self, url_prefix=url_prefix, view_kwargs=view_kwargs)

    def _add_url_rule(
            self,
            rule,
            endpoint=None,
            view_func=None,
            provide_automatic_options=None,
            **options,
    ) -> None:
        self.add_url_rule(rule, endpoint, view_func, provide_automatic_options, **options)

    def _collect_openapi_info(
            self,
            rule: str,
            func: Callable,
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
            doc_ui: bool = True,
            method: str = HTTPMethod.GET
    ) -> ParametersTuple:
        """
        Collects OpenAPI specification information for Flask routes and view functions.

        Args:
            rule: Flask route.
            func: Flask view_func.
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
            method: HTTP method for the operation. Defaults to GET.
        """
        if doc_ui is True:
            # Convert key to string
            new_responses = convert_responses_key_to_string(responses or {})

            # Global response: combine API responses
            combine_responses = {**self.responses, **new_responses}

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
            operation.operationId = operation_id or self.operation_id_callback(
                name=func.__name__, path=rule, method=method
            )

            # Only set `deprecated` if True, otherwise leave it as None
            if deprecated is not None:
                operation.deprecated = deprecated

            # Add security
            if security:
                operation.security = security

            # Add servers
            if servers:
                operation.servers = servers

            # Store tags
            parse_and_store_tags(tags or [], self.tags, self.tag_names, operation)

            # Parse response
            get_responses(combine_responses, self.components_schemas, operation)

            # Convert a route parameter format from /pet/<petId> to /pet/{petId}
            uri = re.sub(r"<([^<:]+:)?", "{", rule).replace(">", "}")

            # Parse method
            parse_method(uri, method, self.paths, operation)

            # Parse parameters
            return parse_parameters(func, components_schemas=self.components_schemas, operation=operation)
        else:
            return parse_parameters(func, doc_ui=False)
