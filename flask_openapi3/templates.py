# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/2/16 9:46


openapi_html_string = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>APIdoc</title>
    <link rel="shortcut icon" href="
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAkBJREFUSEutlU9oE1EQxr/ZPdiDRBR6K
KIepAhevFqwZqNByT+ziaQevEQRUQ8eBQ9iCyLkJFiKJ21FRLCY3SbZpSoxT4sWBQ/24MEe9OJdiURrd3dka9XUNtm31Xd8M/P9ZubNe48Qcg0W7F4sLPY5
GxbmZyeHvgaFU5BDu13Tq8Mg5fLy3kciuv5N/TLaDSQNiOVr55hp7O+EiGiOPb4mzNTEWslKAfy2qA7PAtjZsWLChCinTqxKQKZFWs46A+BGkC+BJhtGcqj
dT6qCWM6+z+BCEADAJ2GkNocCaMVGDz63AqfFF2Xg3VMjtSsU4IBuH/KIH0pkDxCuiHLqUiiApltFEMaDAMQ82jDT50MfclS3LhLhancA3RZGsriuMY1la4
dZoenOAK4LIx3vZA+cokTCjrR6+D0BW1aLcNNljs+YmVfrBviBWt4aB2ONFpAQRjLWrX2BFSwBVr5BbXr/CNh/tNqveGoJ4FynLF3X2TNTyc6FbpGWt4+Bu
QRgR9cJItwU5dSpUICobpWIcCFo9v/Y+e6i6559Xsk2u96DeOHxJsf5fg9AQl582ZPwUiXldP1BYkW7fh9yvFDZ7jhqjYGtRJgH00Zm3kaESAjYB8Xj40+m
0i9+xQROUaeXlEC3mN07vhApFGGmAYD2Al6/x97JZ+aRR0s2mey0nOX/Bf6f8HOxFxNmRsjESgEG89N9KrtvAPSCvRFhZoZlxKUr8B2jujVGwEDT9fa9rmZ
a/x3gCx7M2rvrU8m3suK+3w+AcssZ50vnfwAAAABJRU5ErkJggg==
    ">
    <style>
        body {
            background-color: #131417;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            grid-gap: 36px;
        }

        .box {
            grid-column: span 2;
            width: 300px;
            height: 200px;
            background: #2c303a;
            border-radius: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            transform: scale(1);
            transition: all .3s ease;
        }

        /* Dealing with 2 orphan items */

        .box:last-child:nth-child(3n - 1) {
            grid-column-end: -2;
        }

        .box:nth-last-child(2):nth-child(3n + 1) {
            grid-column-end: 4;
        }

        /* Dealing with single orphan */

        .box:last-child:nth-child(3n - 2) {
            grid-column-end: 5;
        }

        .box:hover {
            transform: scale(1.1);
            box-shadow: 0 0 20px #333743f0;
        }

        .box a {
            color: white;
            font-size: 30px;
            user-select: none;
        }

        .box img {
            user-select: none;
            height: 64px;
            margin-bottom: 10px;
        }

    </style>

</head>
<body>
<div class="grid">
    {% for ui in ui_templates %}
    <div class="box" onclick="window.location.href='{{ ui.name }}';return false">
        <img height="64" src="{{ ui.name }}/images/{{ ui.name }}.svg">
        <a>{{ ui.display_name }}</a>
    </div>
    {% else %}
    <div style="color: white; grid-column: span 2; display: flex; flex-direction: column; grid-column-end: 5;">
        <p>Please install at least one optional UI:</p>
        <p style="font-family: Consolas; background-color: #404348; border-radius: 5px; padding: 5px; font-size: 12px">
        $ pip install -U flask-openapi3[swagger,redoc,rapidoc,rapipdf,scalar,elements]
        </p>
        <p>More optional ui templates goto the document about
        <a href="https://luolingchun.github.io/flask-openapi3/latest/Usage/UI_Templates/" style="color: #0969da">
        UI_Templates.
        </a>
        </p>
    </div>
    {% endfor %}
</div>

</body>
</html>
"""
