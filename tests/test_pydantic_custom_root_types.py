# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/2/27 16:53
from typing import Any

import pytest
from pydantic import BaseModel, RootModel

from flask_openapi3 import OpenAPI, Tag

app = OpenAPI(__name__)
app.config["TESTING"] = True


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
        "extra": "allow",
    }


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.post('/api/v1/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')],
          responses={'200': SelloutList}
          )
def post_sellout(body: SelloutList):
    print(body)
    return body.model_dump_json()


@app.post('/api/v2/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')],
          responses={'200': SelloutDict}
          )
def post_sellout2(body: SelloutDict):
    print(body)
    return body.model_dump_json()


@app.post('/api/v3/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')]
          )
def post_sellout3(body: SelloutDict2):
    print(body)
    return body.model_dump_json()


@app.post('/api/v4/sellouts',
          tags=[Tag(name='Sellout', description='Loren.')]
          )
def post_sellout4(body: SelloutDict3):
    print(body)
    return body.model_dump_json()


def test_v1_sellouts(client):
    resp = client.post("/api/v1/sellouts", json=[{"a": "string", "b": 0}])
    assert resp.status_code == 200


def test_v2_sellouts(client):
    resp = client.post("/api/v2/sellouts", json={"additionalProp1": {"a": "string", "b": 0}})
    assert resp.status_code == 200


def test_v3_sellouts(client):
    resp = client.post("/api/v3/sellouts", json={"a": 11, "b": 23, "c": {"cc": 33, "ccc": 333}})
    assert resp.status_code == 200


def test_v4_sellouts(client):
    resp = client.post("/api/v4/sellouts", json={"a": 11, "b": 23, "c": {"cc": 33, "ccc": 333}})
    assert resp.status_code == 200
