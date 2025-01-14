## tags

You can also specify tag for apis like this:

```python hl_lines="3 6"
from flask_openapi3 import Tag

book_tag = Tag(name='book', description='Some Book')


@api.get('/book', tags=[book_tag])
def get_book():
    ...
```

and then you will get the magic.

![image-20210525160744617](../assets/image-20210525160744617.png)

## abp_tags & view_tags

You don't need to specify **tags** for every api.

```python hl_lines="3 4"
tag = Tag(name='book', description="Some Book")

api = APIBlueprint('/book', __name__, url_prefix='/api', abp_tags=[tag])
api_view = APIView('/book', __name__, url_prefix='/api', view_tags=[tag])


@api.post('/book')
def create_book(body: BookBody):
    ...
```

## summary and description

You need to add docs to the view-func. The first line is the **summary**, and the rest is the **description**. Like this:

```python hl_lines="3 4 5 6"
@app.get('/book/<int:bid>', tags=[book_tag], responses={200: BookResponse}, security=security)
def get_book(path: BookPath, query: BookBody):
    """Get book
    Get some book by id, like:
    http://localhost:5000/book/3
    """
    return {"code": 0, "message": "ok", "data": {"bid": path.bid, "age": query.age, "author": query.author}}
```

![image-20210605115557426](../assets/image-20210605115557426.png)

Now keyword parameters `summary` and `description` is supported, it will be take first.

```python hl_lines="1"
@app.get('/book/<int:bid>', summary="new summary", description='new description')
def get_book(path: BookPath, query: BookBody):
    """Get book
    Get some book by id, like:
    http://localhost:5000/book/3
    """
    return {"code": 0, "message": "ok", "data": {}}
```

![Snipaste_2022-03-19_15-10-06.png](../assets/Snipaste_2022-03-19_15-10-06.png)

## external_docs

Allows referencing an external resource for extended documentation.

More information to see [External Documentation Object](https://spec.openapis.org/oas/v3.1.0#external-documentation-object).

```python hl_lines="10"
from flask_openapi3 import OpenAPI, ExternalDocumentation

app = OpenAPI(__name__, info=info)

@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    summary='new summary',
    description='new description',
    external_docs=ExternalDocumentation(
        url="https://www.openapis.org/",
        description="Something great got better, get excited!")
)
def get_book(path: BookPath):
    ...
```

## operation_id

You can set `operation_id` for an api (operation). The default is automatically.

```python hl_lines="6"
@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    summary='new summary',
    description='new description',
    operation_id="get_book_id"
)
def get_book(path: BookPath):
    ...
```

## operation_id_callback

You can set a custom callback to automatically set `operation_id` for an api (operation).
Just add a `operation_id_callback` param to the constructor of  `OpenAPI` or `APIBlueprint` or `APIView`.
The example shows setting the default `operation_id` to be the function name, in this case `create_book`.

```python hl_lines="6"
def get_operation_id_for_path(*, name: str, path: str, method: str) -> str:
    return name

api = APIBlueprint('book', __name__, url_prefix='/api', operation_id_callback=get_operation_id_for_path)

@api.post('/book/')
def create_book(body: BookBody):
    ...
```

## deprecated

`deprecated`: mark as deprecated support. default to not True.

```python
@app.get('/book', deprecated=True)
def get_books(query: BookQuery):
    ...
```

## security

pass the **security** to your api, like this:

```python hl_lines="1"
@app.get('/book/<int:bid>', tags=[book_tag], security=security)
def get_book(path: Path, query: BookBody):
    ...
```

There are many kinds of security supported here:

```python
# Basic Authentication Sample
basic = {
  "type": "http",
  "scheme": "basic"
}
# JWT Bearer Sample
jwt = {
  "type": "http",
  "scheme": "bearer",
  "bearerFormat": "JWT"
}
# API Key Sample
api_key = {
  "type": "apiKey",
  "name": "api_key",
  "in": "header"
}
# Implicit OAuth2 Sample
oauth2 = {
  "type": "oauth2",
  "flows": {
    "implicit": {
      "authorizationUrl": "https://example.com/api/oauth/dialog",
      "scopes": {
        "write:pets": "modify pets in your account",
        "read:pets": "read your pets"
      }
    }
  }
}
security_schemes = {"jwt": jwt, "api_key": api_key, "oauth2": oauth2, "basic": basic}

app = OpenAPI(__name__, info=info, security_schemes=security_schemes)

security = [
    {"jwt": []},
    {"oauth2": ["write:pets", "read:pets"]},
    {"basic": []}
]

@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    summary='new summary',
    description='new description',
    security=security
)
def get_book(path: BookPath):
    ...
```

## abp_security & view_security

You don't need to specify **security** for every api.

```python hl_lines="3 4"
tag = Tag(name='book', description="Some Book")
security = [{"jwt": []}]
api = APIBlueprint('/book', __name__, abp_tags=[tag], abp_security=security)
api_view = APIView('/book', __name__, abp_tags=[tag], view_security=security)


@api.post('/book')
def create_book(body: BookBody):
    ...
```

## servers

An array of Server Objects, which provide connectivity information to a target server. If the server's property is not provided, or is an empty array, the default value would be a Server Object with an url value of /.

```python
from flask_openapi3 import OpenAPI, Server

app = OpenAPI(__name__, info=info)

@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    summary='new summary',
    description='new description',
    servers=[Server(url="https://www.openapis.org/", description="openapi")]
)
def get_book(path: BookPath):
    ...
```

## openapi_extensions

While the OpenAPI Specification tries to accommodate most use cases, 
additional data can be added to extend the specification at certain points.
See [Specification Extensions](https://spec.openapis.org/oas/v3.1.0#specification-extensions).


```python  hl_lines="3 12 19 28 42"
from flask_openapi3 import OpenAPI, APIBlueprint, APIView

app = OpenAPI(__name__, openapi_extensions={
    "x-google-endpoints": [
        {
            "name": "my-cool-api.endpoints.my-project-id.cloud.goog",
            "allowCors": True
        }
    ]
})

openapi_extensions = {
    "x-google-backend": {
        "address": "https://<NODE_SERVICE_ID>-<HASH>.a.run.app",
        "protocol": "h2"
    }
}

@app.get("/", openapi_extensions=openapi_extensions)
def hello():
    return "ok"


# APIBlueprint
api = APIBlueprint("book", __name__, url_prefix="/api")


@api.get('/book', openapi_extensions=openapi_extensions)
def get_book():
    return {"code": 0, "message": "ok"}


app.register_api(api)

# APIView
api_view = APIView()


@api_view.route("/view/book")
class BookListAPIView:

    @api_view.doc(openapi_extensions=openapi_extensions)
    def post(self):
        return "ok"


app.register_api_view(api_view)
```

## request_body_description

A brief description of the request body.

```python
from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)

@app.post(
    "/",
    request_body_description="A brief description of the request body."
)
def create_book(body: Bookbody):
    ...
```

![](../assets/Snipaste_2025-01-14_10-56-40.png)

## request_body_required

Determines if the request body is required in the request.

## doc_ui

You can pass `doc_ui=False` to disable the `OpenAPI spec` when init `OpenAPI `.

```python
app = OpenAPI(__name__, info=info, doc_ui=False)
```

You can also use `doc_ui` in endpoint or when initializing `APIBlueprint`.

```python hl_lines="4 9"
api = APIBlueprint(
    '/book',
    __name__,
    doc_ui=False
)

# or

@api.get('/book', doc_ui=False)
def get_book():
    ...
```
