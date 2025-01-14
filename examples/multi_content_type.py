# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/12/27 15:30
from flask import Request
from pydantic import BaseModel

from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)


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


@app.post("/a", responses={200: DogBody | CatBody | ContentTypeModel | BsonModel})
def index_a(body: DogBody | CatBody | ContentTypeModel | BsonModel):
    """
    multiple content types examples.

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
            from bson import BSON

            obj = BSON(body.data).decode()
            new_body = body.model_validate(obj=obj)
            print(new_body)
    else:
        # DogBody or CatBody
        ...
    return {"hello": "world"}


if __name__ == '__main__':
    app.run(debug=True)
