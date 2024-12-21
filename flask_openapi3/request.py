# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/1 16:54
import json
from json import JSONDecodeError
from typing import Any, Type, Optional

from flask import request, current_app, abort
from pydantic import ValidationError, BaseModel
from pydantic.fields import FieldInfo
from werkzeug.datastructures.structures import MultiDict


def _get_list_value(model: Type[BaseModel], args: MultiDict, model_field_key: str, model_field_value: FieldInfo):
    if model_field_value.alias and model.model_config.get("populate_by_name"):
        key = model_field_value.alias
        value = args.getlist(model_field_value.alias) or args.getlist(model_field_key)
    elif model_field_value.alias:
        key = model_field_value.alias
        value = args.getlist(model_field_value.alias)
    else:
        key = model_field_key
        value = args.getlist(model_field_key)

    return key, value


def _get_value(model: Type[BaseModel], args: MultiDict, model_field_key: str, model_field_value: FieldInfo):
    if model_field_value.alias and model.model_config.get("populate_by_name"):
        key = model_field_value.alias
        value = args.get(model_field_value.alias) or args.get(model_field_key)
    elif model_field_value.alias:
        key = model_field_value.alias
        value = args.get(model_field_value.alias)
    else:
        key = model_field_key
        value = args.get(model_field_key)

    return key, value


def _validate_header(header: Type[BaseModel], func_kwargs: dict):
    request_headers = dict(request.headers)
    header_dict = {}
    model_properties = header.model_json_schema().get("properties", {})
    for model_field_key, model_field_value in header.model_fields.items():
        key_title = model_field_key.replace("_", "-").title()
        model_field_schema = model_properties.get(model_field_value.alias or model_field_key)
        if model_field_value.alias and header.model_config.get("populate_by_name"):
            key = model_field_value.alias
            key_alias_title = model_field_value.alias.replace("_", "-").title()
            value = request_headers.get(key_alias_title) or request_headers.get(key_title)
        elif model_field_value.alias:
            key = model_field_value.alias
            key_alias_title = model_field_value.alias.replace("_", "-").title()
            value = request_headers.get(key_alias_title)
        else:
            key = model_field_key
            value = request_headers[key_title]
        if value is not None:
            header_dict[key] = value
        if model_field_schema.get("type") == "null":
            header_dict[key] = value  # type:ignore
    # extra keys
    for key, value in request_headers.items():
        if key not in header_dict.keys():
            header_dict[key] = value
    func_kwargs["header"] = header.model_validate(obj=header_dict)


def _validate_cookie(cookie: Type[BaseModel], func_kwargs: dict):
    request_cookies = dict(request.cookies)
    func_kwargs["cookie"] = cookie.model_validate(obj=request_cookies)


def _validate_path(path: Type[BaseModel], path_kwargs: dict, func_kwargs: dict):
    func_kwargs["path"] = path.model_validate(obj=path_kwargs)


def _validate_query(query: Type[BaseModel], func_kwargs: dict):
    request_args = request.args
    query_dict = {}
    model_properties = query.model_json_schema().get("properties", {})
    for model_field_key, model_field_value in query.model_fields.items():
        model_field_schema = model_properties.get(model_field_value.alias or model_field_key)
        if model_field_schema.get("type") == "array":
            key, value = _get_list_value(query, request_args, model_field_key, model_field_value)
        else:
            key, value = _get_value(query, request_args, model_field_key, model_field_value)
        if value is not None and value != []:
            query_dict[key] = value
        if model_field_schema.get("type") == "null":
            query_dict[key] = value
    # extra keys
    for key, value in request_args.items():
        if key not in query_dict.keys():
            query_dict[key] = value
    func_kwargs["query"] = query.model_validate(obj=query_dict)


def _validate_form(form: Type[BaseModel], func_kwargs: dict):
    request_form = request.form
    request_files = request.files
    form_dict = {}
    model_properties = form.model_json_schema().get("properties", {})
    for model_field_key, model_field_value in form.model_fields.items():
        model_field_schema = model_properties.get(model_field_value.alias or model_field_key)
        if model_field_schema.get("type") == "array":
            if model_field_schema.get("items") == {"format": "binary", "type": "string"}:
                # list[FileStorage]
                key, value = _get_list_value(form, request_files, model_field_key, model_field_value)
            else:
                value = []
                key, value_list = _get_list_value(form, request_form, model_field_key, model_field_value)
                for _value in value_list:
                    try:
                        value.append(json.loads(_value))
                    except (JSONDecodeError, TypeError):
                        value.append(_value)
        elif model_field_schema.get("type") == "string" and model_field_schema.get("format") == "binary":
            # FileStorage
            key, value = _get_value(form, request_files, model_field_key, model_field_value)
        else:
            key, _value = _get_value(form, request_form, model_field_key, model_field_value)
            try:
                value = json.loads(_value)
            except (JSONDecodeError, TypeError):
                value = _value
        if value is not None and value != []:
            form_dict[key] = value
        if model_field_schema.get("type") == "null":
            form_dict[key] = value
    # extra keys
    for key, value in {**dict(request_form), **dict(request_files)}.items():
        if key not in form_dict.keys():
            form_dict[key] = value
    func_kwargs["form"] = form.model_validate(obj=form_dict)


def _validate_body(body: Type[BaseModel], func_kwargs: dict):
    obj = request.get_json(silent=True)
    if isinstance(obj, str):
        body_model = body.model_validate_json(json_data=obj)
    else:
        body_model = body.model_validate(obj=obj)
    func_kwargs["body"] = body_model


def _validate_request(
        header: Optional[Type[BaseModel]] = None,
        cookie: Optional[Type[BaseModel]] = None,
        path: Optional[Type[BaseModel]] = None,
        query: Optional[Type[BaseModel]] = None,
        form: Optional[Type[BaseModel]] = None,
        body: Optional[Type[BaseModel]] = None,
        raw: Optional[Type[BaseModel]] = None,
        path_kwargs: Optional[dict[Any, Any]] = None
) -> dict:
    """
    Validate requests and responses.

    Args:
        header: Header model.
        cookie: Cookie model.
        path: Path model.
        query: Query model.
        form: Form model.
        body: Body model.
        path_kwargs: Path parameters.

    Returns:
        dict: Request kwargs.

    Raises:
        ValidationError: If validation fails.
    """

    # Dictionary to store func kwargs
    func_kwargs: dict = {}

    try:
        # Validate header, cookie, path, and query parameters
        if header:
            _validate_header(header, func_kwargs)
        if cookie:
            _validate_cookie(cookie, func_kwargs)
        if path:
            _validate_path(path, path_kwargs or {}, func_kwargs)
        if query:
            _validate_query(query, func_kwargs)
        if form:
            _validate_form(form, func_kwargs)
        if body:
            _validate_body(body, func_kwargs)
        if raw:
            func_kwargs["raw"] = request
    except ValidationError as e:
        # Create a response with validation error details
        validation_error_callback = getattr(current_app, "validation_error_callback")
        abort(validation_error_callback(e))

    return func_kwargs
