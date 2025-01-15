# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2025/1/15 9:58
import pytest

from flask_openapi3 import APIBlueprint, OpenAPI, APIView

app = OpenAPI(__name__, )
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


api1 = APIBlueprint("/book1", __name__, url_prefix="/api")
api2 = APIBlueprint("/book2", __name__)


@api1.get("/book")
def create_book1():
    return "ok"


@api2.get("/book")
def create_book2():
    return "ok"


app.register_api(api1, url_prefix="/api1")
app.register_api(api2, url_prefix="/api2")

api_view1 = APIView(url_prefix="/api")
api_view2 = APIView()


@api_view1.route("/book")
class BookAPIView:
    @api_view1.doc(summary="get book")
    def get(self):
        return "ok"


@api_view2.route("/book")
class BookAPIView2:
    @api_view2.doc(summary="get book")
    def get(self, ):
        return "ok"


app.register_api_view(api_view1, url_prefix="/api3")
app.register_api_view(api_view2, url_prefix="/api4")


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    _json = resp.json
    assert "/api1/book" in _json["paths"].keys()
    assert "/api2/book" in _json["paths"].keys()
    assert "/api3/book" in _json["paths"].keys()
    assert "/api4/book" in _json["paths"].keys()
