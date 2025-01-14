# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/11/10 12:17
from pydantic import ValidationError

from flask_openapi3 import OpenAPI, Server, ServerVariable, ExternalDocumentation


def test_server_variable():
    Server(
        url="http://127.0.0.1:5000",
        variables=None
    )
    error = 0
    try:
        variables = {"one": ServerVariable(default="one", enum=[])}
    except ValidationError:
        error = 1
    assert error == 1
    variables = {"one": ServerVariable(default="one")}
    Server(
        url="http://127.0.0.1:5000",
        variables=variables
    )
    error = 0
    assert error == 0
    variables = {"one": ServerVariable(default="one", enum=["one", "two"])}
    Server(
        url="http://127.0.0.1:5000",
        variables=variables
    )
    error = 0
    assert error == 0

    app = OpenAPI(
        __name__,
        servers=[Server(
            url="http://127.0.0.1:5000",
            variables=None
        )],
        external_docs=ExternalDocumentation(
            url="https://www.openapis.org/",
            description="Something great got better, get excited!")
    )

    assert "servers" in app.api_doc
    assert "externalDocs" in app.api_doc
