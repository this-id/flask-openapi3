# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2025/1/6 16:37
from typing import Union

import pytest
from flask import Request
from pydantic import BaseModel

from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


class DogBody(BaseModel):
    a: int = None
    b: str = None

    model_config = {
        "openapi_extra": {
            "content_type": "application/vnd.dog+json"
        }
    }


class CatBody(BaseModel):
    c: int = None
    d: str = None

    model_config = {
        "openapi_extra": {
            "content_type": "application/vnd.cat+json"
        }
    }


class BsonModel(BaseModel):
    e: int = None
    f: str = None

    model_config = {
        "openapi_extra": {
            "content_type": "application/bson"
        }
    }


class ContentTypeModel(BaseModel):
    model_config = {
        "openapi_extra": {
            "content_type": "text/csv"
        }
    }


@app.post("/a", responses={200: Union[DogBody, CatBody, ContentTypeModel, BsonModel]})
def index_a(body: Union[DogBody, CatBody, ContentTypeModel, BsonModel]):
    """
    This may be confusing, if the content-type is application/json, the type of body will be auto parsed to
    DogBody or CatBody, otherwise it cannot be parsed to ContentTypeModel or BsonModel.
    The body is equivalent to the request variable in Flask, and you can use body.data, body.text, etc ...
    """
    print(body)
    if isinstance(body, Request):
        if body.mimetype == "text/csv":
            # processing csv data
            ...
        elif body.mimetype == "application/bson":
            # processing bson data
            ...
    else:
        # DogBody or CatBody
        ...
    return {"hello": "world"}


@app.post("/b", responses={200: Union[ContentTypeModel, BsonModel]})
def index_b(body: Union[ContentTypeModel, BsonModel]):
    """
    This may be confusing, if the content-type is application/json, the type of body will be auto parsed to
    DogBody or CatBody, otherwise it cannot be parsed to ContentTypeModel or BsonModel.
    The body is equivalent to the request variable in Flask, and you can use body.data, body.text, etc ...
    """
    print(body)
    if isinstance(body, Request):
        if body.mimetype == "text/csv":
            # processing csv data
            ...
        elif body.mimetype == "application/bson":
            # processing bson data
            ...
    else:
        # DogBody or CatBody
        ...
    return {"hello": "world"}


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200

    resp = client.post("/a", json={"a": 1, "b": "2"})
    assert resp.status_code == 200

    resp = client.post("/a", data="a,b,c\n1,2,3", headers={"Content-Type": "text/csv"})
    assert resp.status_code == 200
