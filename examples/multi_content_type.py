# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/12/27 15:30
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


class ContentTypeModel(BaseModel):
    model_config = {
        "openapi_extra": {
            "content_type": "text/csv"
        }
    }


@app.post("/a", responses={200: DogBody | CatBody | ContentTypeModel})
def index_a(body: DogBody | CatBody | ContentTypeModel):
    print(body)
    return {"hello": "world"}


if __name__ == '__main__':
    app.run(debug=True)
