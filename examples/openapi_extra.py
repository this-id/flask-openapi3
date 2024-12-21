# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/6/1 15:04
from pydantic import BaseModel

from flask_openapi3 import OpenAPI, FileStorage

app = OpenAPI(__name__)


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


@app.post('/upload/files')
def upload_files(form: UploadFilesForm):
    print(form.file)
    print(form.str_list)
    return {"code": 0, "message": "ok"}


@app.post('/book', )
def create_book(body: BookBody):
    print(body)
    return {"code": 0, "message": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
