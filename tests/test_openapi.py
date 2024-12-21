from __future__ import annotations

from typing import Generic, TypeVar, Optional, Literal

from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI

T = TypeVar("T", bound=BaseModel)


def test_responses_are_replicated_in_open_api(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    class BaseResponse(BaseModel):
        """Base description"""
        test: int

        model_config = dict(
            openapi_extra={
                "description": "Custom description",
                "headers": {
                    "location": {
                        "description": "URL of the new resource",
                        "schema": {"type": "string"}
                    }
                },
                "content": {
                    "text/plain": {
                        "schema": {"type": "string"}
                    }
                },
                "links": {
                    "dummy": {
                        "description": "dummy link"
                    }
                }
            }
        )

    @test_app.get("/test", responses={"201": BaseResponse})
    def endpoint_test():
        return b"", 201  # pragma: no cover

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["get"]["responses"]["201"] == {
            "description": "Custom description",
            "headers": {
                "location": {
                    "description": "URL of the new resource",
                    "schema": {"type": "string"}
                }
            },
            "content": {
                # This content is coming from responses
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/BaseResponse"}
                },
                # While this one comes from responses
                "text/plain": {
                    "schema": {"type": "string"}
                }
            },
            "links": {
                "dummy": {
                    "description": "dummy link"
                }
            }
        }


def test_none_responses_are_replicated_in_open_api(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.get(
        "/test",
        responses={
            "204": {
                "description": "Custom description",
                "headers": {
                    "x-my-special-header": {
                        "description": "Custom header",
                        "schema": {"type": "string"}
                    }
                },
                "content": {
                    "text/plain": {
                        "schema": {"type": "string"}
                    }
                },
                "links": {
                    "dummy": {
                        "description": "dummy link"
                    }
                }
            }
        }
    )
    def endpoint_test():
        return b"", 204  # pragma: no cover

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["get"]["responses"]["204"] == {
            "description": "Custom description",
            "headers": {
                "x-my-special-header": {
                    "description": "Custom header",
                    "schema": {"type": "string"}
                }
            },
            "content": {
                "text/plain": {
                    "schema": {"type": "string"}
                }
            },
            "links": {
                "dummy": {
                    "description": "dummy link"
                }
            }
        }


def test_responses_are_replicated_in_open_api2(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.get(
        "/test",
        responses={
            "201": {
                "description": "Custom description",
                "headers": {
                    "location": {
                        "description": "URL of the new resource",
                        "schema": {"type": "string"}
                    }
                },
                "content": {
                    "text/plain": {
                        "schema": {"type": "string"}
                    }
                },
                "links": {
                    "dummy": {
                        "description": "dummy link"
                    }
                }
            }
        }
    )
    def endpoint_test():
        return b"", 201  # pragma: no cover

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["get"]["responses"]["201"] == {
            "description": "Custom description",
            "headers": {
                "location": {
                    "description": "URL of the new resource",
                    "schema": {"type": "string"}
                }
            },
            "content": {
                "text/plain": {
                    "schema": {"type": "string"}
                }
            },
            "links": {
                "dummy": {
                    "description": "dummy link"
                }
            }
        }


def test_responses_without_content_are_replicated_in_open_api(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.get(
        "/test",
        responses={
            "201": {
                "description": "Custom description",
                "headers": {
                    "location": {
                        "description": "URL of the new resource",
                        "schema": {"type": "string"}
                    }
                },
                "links": {
                    "dummy": {
                        "description": "dummy link"
                    }
                }
            }
        }
    )
    def endpoint_test():
        return b"", 201  # pragma: no cover

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["get"]["responses"]["201"] == {
            "description": "Custom description",
            "headers": {
                "location": {
                    "description": "URL of the new resource",
                    "schema": {"type": "string"}
                }
            },
            "links": {
                "dummy": {
                    "description": "dummy link"
                }
            }
        }


class BaseRequest(BaseModel):
    """Base description"""
    test_int: int
    test_str: str


class BaseRequestGeneric(BaseModel, Generic[T]):
    detail: T

    model_config = dict(
        openapi_extra={
            "examples": {
                "Example 01": {
                    "summary": "An example",
                    "value": {
                        "test_int": -1,
                        "test_str": "negative",
                    }
                },
                "Example 02": {
                    "externalValue": "https://example.org/examples/second-example.xml"
                },
                "Example 03": {
                    "$ref": "#/components/examples/third-example"
                }
            }
        }
    )


def test_body_examples_are_replicated_in_open_api(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test")
    def endpoint_test(body: BaseRequestGeneric[BaseRequest]):
        return body.model_dump(), 200

    with test_app.test_client() as client:
        client.post("/test", json={"detail": {"test_int": 1, "test_str": "s"}})
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["post"]["requestBody"] == {
            "content": {
                "application/json": {
                    "examples": {
                        "Example 01": {"summary": "An example", "value": {"test_int": -1, "test_str": "negative"}},
                        "Example 02": {"externalValue": "https://example.org/examples/second-example.xml"},
                        "Example 03": {"$ref": "#/components/examples/third-example"}
                    },
                    "schema": {"$ref": "#/components/schemas/BaseRequestGeneric_BaseRequest_"}
                }
            },
            "required": True
        }
        assert resp.json["components"]["schemas"]["BaseRequestGeneric_BaseRequest_"] == {
            "properties": {"detail": {"$ref": "#/components/schemas/BaseRequest"}},
            "required": ["detail"],
            "title": "BaseRequestGeneric[BaseRequest]",
            "type": "object",
        }


def test_form_examples(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    model_config = dict(
        openapi_extra={
            "examples": {
                "Example 01": {
                    "summary": "An example",
                    "value": {
                        "test_int": -1,
                        "test_str": "negative",
                    }
                }
            }
        }
    )
    BaseRequestGeneric[BaseRequest].model_config = model_config

    @test_app.post("/test")
    def endpoint_test(form: BaseRequestGeneric[BaseRequest]):
        return form.model_dump(), 200  # pragma: no cover

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["post"]["requestBody"] == {
            "content": {
                "multipart/form-data": {
                    "schema": {"$ref": "#/components/schemas/BaseRequestGeneric_BaseRequest_"},
                    "examples": {
                        "Example 01": {"summary": "An example", "value": {"test_int": -1, "test_str": "negative"}}
                    }
                }
            },
            "required": True
        }
        assert resp.json["components"]["schemas"]["BaseRequestGeneric_BaseRequest_"] == {
            "properties": {"detail": {"$ref": "#/components/schemas/BaseRequest"}},
            "required": ["detail"],
            "title": "BaseRequestGeneric[BaseRequest]",
            "type": "object",
        }


class BaseRequestBody(BaseModel):
    base: BaseRequest


def test_body_with_complex_object(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test")
    def endpoint_test(body: BaseRequestBody):
        return body.model_dump(), 200  # pragma: no cover

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert {"properties", "required", "title", "type"} == set(
            resp.json["components"]["schemas"]["BaseRequestBody"].keys())


class Detail(BaseModel):
    num: int


class GenericResponse(BaseModel, Generic[T]):
    detail: T


class ListGenericResponse(BaseModel, Generic[T]):
    items: list[GenericResponse[T]]


def test_responses_with_generics(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.get("/test", responses={"201": ListGenericResponse[Detail]})
    def endpoint_test():
        return b"", 201  # pragma: no cover

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["get"]["responses"]["201"] == {
            "description": "Created",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ListGenericResponse_Detail_"}
                },
            },
        }

        schemas = resp.json["components"]["schemas"]
        detail = schemas["ListGenericResponse_Detail_"]
        assert detail["title"] == "ListGenericResponse[Detail]"
        assert detail["properties"]["items"]["items"]["$ref"] == "#/components/schemas/GenericResponse_Detail_"
        assert schemas["GenericResponse_Detail_"]["title"] == "GenericResponse[Detail]"


class PathParam(BaseModel):
    type_name: str = Field(..., description="id for path", max_length=300,
                           json_schema_extra={"deprecated": False, "example": "42"})


def test_path_parameter_object(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test")
    def endpoint_test(path: PathParam):
        return path.model_dump(), 200  # pragma: no cover

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["post"]["parameters"][0] == {
            "deprecated": False,
            "description": "id for path",
            "example": "42",
            "in": "path",
            "name": "type_name",
            "required": True,
            "schema": {
                "deprecated": False,
                "description": "id for path",
                "maxLength": 300,
                "example": "42",
                "title": "Type Name",
                "type": "string",
            },
        }


class QueryParam(BaseModel):
    count: int = Field(..., description="count of param", le=1000.0,
                       json_schema_extra={"deprecated": True, "example": 100})


def test_query_parameter_object(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test")
    def endpoint_test(query: QueryParam):
        return query.model_dump(), 200  # pragma: no cover

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["post"]["parameters"][0] == {
            "deprecated": True,
            "description": "count of param",
            "example": 100,
            "in": "query",
            "name": "count",
            "required": True,
            "schema": {
                "deprecated": True,
                "description": "count of param",
                "maximum": 1000.0,
                "example": 100,
                "title": "Count",
                "type": "integer",
            },
        }


class HeaderParam(BaseModel):
    app_name: str = Field(None, description="app name")


class CookieParam(BaseModel):
    app_name: str = Field(None, description="app name", json_schema_extra={"example": "aaa"})


def test_header_parameter_object(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test")
    def endpoint_test(header: HeaderParam, cookie: CookieParam):
        print(header, cookie)  # pragma: no cover

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["post"]["parameters"][0] == {
            "description": "app name",
            "in": "header",
            "name": "app_name",
            "required": False,
            "schema": {"description": "app name", "title": "App Name", "type": "string", "default": None}
        }
        assert resp.json["paths"]["/test"]["post"]["parameters"][1] == {
            "description": "app name",
            "in": "cookie",
            "example": "aaa",
            "name": "app_name",
            "required": False,
            "schema": {"description": "app name", "example": "aaa", "title": "App Name", "type": "string",
                       "default": None}
        }


class Model(BaseModel):
    one: Optional[int] = Field(default=None)
    two: Optional[int] = Field(default=2)


def test_default_none(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test")
    def endpoint_test(body: Model):
        print([])  # pragma: no cover

    works = Model.model_json_schema()["properties"]
    assert works["one"]["default"] is None
    assert works["two"]["default"] == 2
    breaks = test_app.api_doc["components"]["schemas"]["Model"]["properties"]
    assert breaks["two"]["default"] == 2
    assert breaks["one"]["default"] is None


def test_parameters_none(request):
    """Parameters key shouldn't exist."""
    test_app = OpenAPI(request.node.name)

    @test_app.post("/test")
    def endpoint_test():
        print([])  # pragma: no cover

    data = test_app.api_doc["paths"]["/test"]["post"]

    assert "parameters" not in data


def test_deprecated_none(request):
    """Parameters key shouldn't exist."""
    test_app = OpenAPI(request.node.name)

    @test_app.post("/test")
    def endpoint_test():
        print([])  # pragma: no cover

    data = test_app.api_doc["paths"]["/test"]["post"]

    assert "deprecated" not in data


class TupleModel(BaseModel):
    my_tuple: tuple[Literal["a", "b"], Literal["c", "d"]]


def test_prefix_items(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test")
    def endpoint_test(body: TupleModel):
        print([])  # pragma: no cover

    schema = test_app.api_doc["paths"]["/test"]["post"]["requestBody"]["content"]["application/json"]["schema"]
    assert schema == {'$ref': '#/components/schemas/TupleModel'}
    components = test_app.api_doc["components"]["schemas"]
    assert components["TupleModel"] == {'properties': {'my_tuple': {'maxItems': 2,
                             'minItems': 2,
                             'prefixItems': [{'enum': ['a', 'b'],
                                              'type': 'string'},
                                             {'enum': ['c', 'd'],
                                              'type': 'string'}],
                             'title': 'My Tuple',
                             'type': 'array'}},
 'required': ['my_tuple'],
 'title': 'TupleModel',
 'type': 'object'}
