# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/6 16:38
from __future__ import annotations

import json
from http import HTTPStatus
from typing import Optional

import pytest
from flask import Response
from pydantic import BaseModel, RootModel, Field

from flask_openapi3 import ExternalDocumentation
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI

info = Info(title='book API', version='1.0.0')

jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}
security_schemes = {"jwt": jwt}


class NotFoundResponse(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Resource not found!", description="Exception Information")


def get_operation_id_for_path_callback(*, name: str, path: str, method: str) -> str:
    print(name, path, method)
    return name


app = OpenAPI(
    __name__,
    info=info,
    security_schemes=security_schemes,
    responses={"404": NotFoundResponse},
    operation_id_callback=get_operation_id_for_path_callback,
)
app.config["TESTING"] = True

security = [{"jwt": []}]
book_tag = Tag(name='book', description='Book')


class BookQuery(BaseModel):
    age: Optional[int] = Field(None, description='Age')


class BookBody(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BookPath(BaseModel):
    bid: int = Field(..., description='book id')


class BookBodyWithID(BaseModel):
    bid: int = Field(..., description='book id')
    age: Optional[int] = Field(None, ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BaseResponse(BaseModel):
    code: int = Field(0, description="Status Code")
    message: str = Field("ok", description="Exception Information")


class BookListResponseV1(BaseResponse):
    data: list[BookBodyWithID] = Field(..., description="All the books")


class BookListResponseV2(BaseModel):
    books: list[BookBodyWithID] = Field(...)


class BookListResponseV3(RootModel):
    root: list[BookBodyWithID]


class BookResponse(BaseModel):
    code: int = Field(0, description="Status Code")
    message: str = Field("ok", description="Exception Information")
    data: BookBodyWithID


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    operation_id="get_book_id",
    external_docs=ExternalDocumentation(
        url="https://www.openapis.org/",
        description="Something great got better, get excited!"),
    responses={"200": BookResponse},
    security=security
)
def get_book(path: BookPath):
    """Get a book
    to get some book by id, like:
    http://localhost:5000/book/3
    """
    if path.bid == 4:
        return NotFoundResponse().model_dump(), 404


@app.get('/book', tags=[book_tag], responses={"200": BookListResponseV1})
def get_books(query: BookBody):
    """get books
    to get all books
    """
    assert query.age == 3
    assert query.author == 'joy'
    return {
        "code": 0,
        "message": "ok",
        "data": [
            {"bid": 1, "age": query.age, "author": "b1"},
            {"bid": 2, "age": query.age, "author": "b2"}
        ]
    }


@app.get('/book_v2', tags=[book_tag], responses={"200": BookListResponseV2})
def get_books_v2(query: BookBody):
    """get books
    to get all books (v2)
    """
    assert query.age == 3
    assert query.author == 'joy'
    return {
        "books": [
            {"bid": 1, "age": query.age, "author": "b1"},
            {"bid": 2, "age": query.age, "author": "b2"}
        ]
    }


@app.get('/book_v3', tags=[book_tag], responses={"200": BookListResponseV3})
def get_books_v3(query: BookBody):
    """get books
    to get all books (v3)
    """
    assert query.age == 3
    assert query.author == 'joy'

    books = [
        {"bid": 1, "age": query.age, "author": "b1"},
        {"bid": 2, "age": query.age, "author": "b2"}
    ]
    # A `list` have to be converted to json-format `str` returned as a `Response` object,
    # because flask doesn't support returning a `list` as a response
    return Response(json.dumps(books), status=200, headers={'Content-Type': 'application/json'})


@app.post('/book', tags=[book_tag], responses={"200": BaseResponse})
def create_book(body: BookBody):
    assert body.age == 3
    return {"code": 0, "message": "ok"}, HTTPStatus.OK


@app.put('/book/<int:bid>', tags=[book_tag])
def update_book(path: BookPath, body: BookBody):
    assert path.bid == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@app.patch('/book/<int:bid>', tags=[book_tag], doc_ui=False)
def update_book1(path: BookPath, body: BookBody):
    assert path.bid == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@app.delete('/book/<int:bid>', tags=[book_tag], responses={"200": BaseResponse})
def delete_book(path: BookPath):
    assert path.bid == 1
    return {"code": 0, "message": "ok"}


@app.delete('/book_no_response/<int:bid>', tags=[book_tag], responses={"204": None})
def delete_book_no_response(path: BookPath):
    assert path.bid == 1
    return b'', 204


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    print(resp.json)
    assert resp.status_code == 200
    assert resp.json == app.api_doc


def test_get(client):
    resp = client.get("/book?age=3&author=joy")
    assert resp.status_code == 200
    resp_v2 = client.get("/book_v2?age=3&author=joy")
    assert resp_v2.status_code == 200
    resp_v3 = client.get("/book_v3?age=3&author=joy")
    assert resp_v3.status_code == 200


def test_get_by_id_4(client):
    resp = client.get("/book/4?age=3&author=joy")
    assert resp.status_code == 404


def test_post(client):
    resp = client.post("/book", json={"age": 3})
    assert resp.status_code == 200


def test_put(client):
    resp = client.put("/book/1", json={"age": 3})
    assert resp.status_code == 200


def test_patch(client):
    resp = client.patch("/book/1", json={"age": 3})
    assert resp.status_code == 200


def test_delete(client):
    resp = client.delete("/book/1")
    assert resp.status_code == 200


def test_delete_no_response(client):
    resp = client.delete("/book_no_response/1")
    assert resp.status_code == 204
