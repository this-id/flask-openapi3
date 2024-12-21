# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/6/30 10:12
import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI, FileStorage

app = OpenAPI(__name__)
app.config["TESTING"] = True


class UploadFilesForm(BaseModel):
    file: FileStorage
    str_list: list[str]

    model_config = dict(
        openapi_extra={
            # "example": {"a": 123},
            "examples": {
                "Example 01": {
                    "summary": "An example",
                    "value": {
                        "file": "Example-01.jpg",
                        "str_list": ["a", "b", "c"]
                    }
                },
                "Example 02": {
                    "summary": "Another example",
                    "value": {
                        "str_list": ["1", "2", "3"]
                    }
                }
            }
        }
    )


class BookBody(BaseModel):
    age: int
    author: str

    model_config = dict(
        openapi_extra={
            "description": "This is post RequestBody",
            "example": {"age": 12, "author": "author1"},
            "examples": {
                "example1": {
                    "summary": "example summary1",
                    "description": "example description1",
                    "value": {
                        "age": 24,
                        "author": "author2"
                    }
                },
                "example2": {
                    "summary": "example summary2",
                    "description": "example description2",
                    "value": {
                        "age": 48,
                        "author": "author3"
                    }
                }

            }}
    )


class MessageResponse(BaseModel):
    message: str = Field(..., description="The message")
    metadata: dict[str, str] = Field(alias="metadata_")

    model_config = dict(
        by_alias=False,
        openapi_extra={
            # "example": {"message": "aaa"},
            "examples": {
                "example1": {
                    "summary": "example1 summary",
                    "value": {
                        "message": "bbb"
                    }
                },
                "example2": {
                    "summary": "example2 summary",
                    "value": {
                        "message": "ccc"
                    }
                }
            }
        }
    )


@app.post("/form")
def api_form(form: UploadFilesForm):
    print(form)  # pragma: no cover


@app.post("/body", responses={"200": MessageResponse})
def api_error_json(body: BookBody):
    print(body)  # pragma: no cover


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    _json = resp.json
    assert resp.status_code == 200
    assert _json["paths"]["/form"]["post"]["requestBody"]["content"]["multipart/form-data"]["examples"] == \
           {
               "Example 01": {
                   "summary": "An example",
                   "value": {
                       "file": "Example-01.jpg",
                       "str_list": ["a", "b", "c"]
                   }
               },
               "Example 02": {
                   "summary": "Another example",
                   "value": {
                       "str_list": ["1", "2", "3"]
                   }
               }
           }
    assert _json["paths"]["/body"]["post"]["requestBody"]["description"] == "This is post RequestBody"
    assert _json["paths"]["/body"]["post"]["requestBody"]["content"]["application/json"]["example"] == \
           {"age": 12, "author": "author1"}
    assert _json["paths"]["/body"]["post"]["responses"]["200"]["content"]["application/json"]["examples"] == \
           {
               "example1": {
                   "summary": "example1 summary",
                   "value": {
                       "message": "bbb"
                   }
               },
               "example2": {
                   "summary": "example2 summary",
                   "value": {
                       "message": "ccc"
                   }
               }
           }
    assert _json["components"]["schemas"]["MessageResponse"]["properties"].get("metadata") is not None
