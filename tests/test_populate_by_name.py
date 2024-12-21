# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/8/31 15:35
from typing import Sequence

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


class BookQuery(BaseModel):
    age: int
    author: str = Field(..., alias="author_name")

    model_config = {"populate_by_name": True}


@app.get("/book", summary="get books")
def get_book(query: BookQuery):
    """
    get all books
    """
    print(query)
    return "ok"


class QueryModel(BaseModel):
    aliased_field: str = Field(alias="aliasedField")

    aliased_list_field: list[str] = Field(alias="aliasedListField")


@app.get("/query-alias-test")
def query_alias_test(query: QueryModel):
    assert query.aliased_field == "test"
    return "ok"


class HeaderModel(BaseModel):
    Hello1: str = Field(..., alias="Hello2")

    model_config = {"populate_by_name": True}


@app.get("/header")
def get_book_header(header: HeaderModel):
    return header.model_dump(by_alias=True)


class TupleModel(BaseModel):
    values: tuple[int, int]
    sequence: Sequence[int] = Field(alias="Sequence")

    model_config = {"populate_by_name": True}


@app.get("/tuple-test")
def tuple_test(query: TupleModel):
    assert query.values == (2, 2)
    return b"", 200


class AliasModel(BaseModel):
    aliased_field: str = Field(alias="aliasedField")


@app.post("/form-alias-test")
def alias_test(form: AliasModel):
    assert form.aliased_field == "test"
    return b"", 200


def test_header(client):
    headers = {"Hello2": "111"}
    resp = client.get("/header", headers=headers)
    print(resp.json)
    assert resp.status_code == 200
    assert resp.json == headers


def test_tuple_query(client):
    resp = client.get(
        "/tuple-test",
        query_string={"values": [2, 2], "sequence": [1, 2, 3]},
    )
    assert resp.status_code == 200


def test_form_alias(client):
    resp = client.post(
        "/form-alias-test",
        data={"aliasedField": "test"},
    )
    assert resp.status_code == 200

    resp = client.post(
        "/form-alias-test",
        data={"aliased_field": "test"},
    )
    assert resp.status_code == 422


def test_query_alias(client):
    resp = client.get(
        "/query-alias-test",
        query_string={"aliasedField": "test", "aliasedListField": ["test"]},
    )
    assert resp.status_code == 200

    resp = client.get(
        "/query-alias-test",
        data={"aliased_field": "test", "aliased_list_field": ["test"]},
    )
    assert resp.status_code == 422


def test_query_populate_by_name(client):
    resp = client.get("/book?age=1&author=aa")
    assert resp.status_code == 200
    resp = client.get("/book?age=1&author_name=aa")
    assert resp.status_code == 200
