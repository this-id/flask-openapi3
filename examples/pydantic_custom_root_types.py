# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/2/27 15:26
from typing import Any

from pydantic import BaseModel, RootModel

from flask_openapi3 import OpenAPI, Tag

app = OpenAPI(__name__)


class Sellout(BaseModel):
    a: str
    b: int


class SelloutList(RootModel):
    root: list[Sellout]


class SelloutDict(RootModel):
    root: dict[str, Sellout]


class SelloutDict2(RootModel):
    root: dict[Any, Any]


class SelloutDict3(BaseModel):
    model_config = {
        "extra": "allow"
    }


@app.post('/api/v1/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')],
          responses={200: SelloutList}
          )
def post_sellout(body: SelloutList):
    print(body)
    return body.model_dump()


@app.post('/api/v2/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')],
          responses={200: SelloutDict}
          )
def post_sellout2(body: SelloutDict):
    print(body)
    return body.model_dump()


@app.post('/api/v3/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')]
          )
def post_sellout3(body: SelloutDict2):
    print(body)
    return body.model_dump()


@app.post('/api/v4/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')]
          )
def post_sellout4(body: SelloutDict3):
    print(body)
    return body.model_dump()


if __name__ == '__main__':
    app.run(debug=True)
