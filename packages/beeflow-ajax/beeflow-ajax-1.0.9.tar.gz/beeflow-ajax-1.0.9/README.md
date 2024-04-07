# BeeflowAjaxPy

The library to maintain ajax and websockets communication without writing complicated code in JS

## Installation

```shell
$ pip install beeflow-ajax
```

```shell
$ npm i @beeflow/beeflow_ajax_js
```

or use cdn

```html

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@beeflow/beeflow_ajax_js@1.0.2/css/BeeflowAjax.css"/>
<script src="https://cdn.jsdelivr.net/npm/@beeflow/beeflow_ajax_js@1.0.2/js/js-url-2.3.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@beeflow/beeflow_ajax_js@1.0.2/js/BeeflowAjax.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@beeflow/beeflow_ajax_js@1.0.2/js/BeeflowAjaxSwalMessages.js"></script>
```

Where

* `css/BeeflowAjax.css` - declaration for classes for IDE helper
* `js/js-url-2.3.0.min.js` - library used by
* `js/BeeflowAjax.js` - beeflow ajax library including websocket
* `js/BeeflowAjaxSwalMessages.js` - definition of messages that use sweet alerts (you need to have sweet alerts library)

## Usage examples - HTML / JavaScript

### Ajax

#### Delete button with confirmation

```html
<a href="https://some.web.example/api/v1/record/<int:record_id>" data-method="delete"
   data-confirm="Are you sure you want to delete this record?"
   class="ajax-link" title="Delete record"
   data-callback="() => { console.log('Hello world!') }">delete</a>
```

#### Form

```html
<form action="https://some.web.example/api/v1/record/" method="post" class="ajax-form">
    <input type="text" name="some_data">
    <input type="submit" name="submit" value="Send">
</form>
```

#### Select

```html
<select data-ajax-datasource="https://some.web.example/api/v1/record/all" data-defaul-value="10"
        data-url-value="language_code=pl"></select>
```

#### Sending data using own script

```javascript
BeeflowAjax.send("https://some.web.example/api/v1/record/", {"some": "data"}, submitButton, callbackMethod, 'POST');
```

### WebSocket

#### Initialisation

```javascript
BeeflowAjax.websocket.init("ws://some.web.example/api/v1/ws/<any:connectionId>", {some: "data"}, () => {
    consolr.log('Callback function')
})
```

#### Form

```html
<form action="https://some.web.example/api/v1/record/" method="post" class="websocket-form">
    <input type="text" name="some_data">
    <input type="submit" name="submit" value="Send">
</form>
```

## Usage examples - Python

### Ajax

##### Django

```python
from django.http import HttpResponse  # or any response class
from rest_framework.views import APIView
from beeflow_ajax.lib import AjaxResponse

...


class SomeView(APIView):
    ajax = AjaxResponse(HttpResponse)

    def get(self, request, id: int, *args, **kwargs):
        return self.ajax.assign("#some-html-element-id", f"Received id: {id}").response(*args, **kwargs)
```

##### FastAPI

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from beeflow_ajax.lib import AjaxResponse

router = APIRouter()


@router.get("/some-view-id", status_code=status.HTTP_200_OK)
async def new_game(db: Session = Depends(get_db)):
    ajax = AjaxResponse()

    # as we didn't pass any response object to the AjaxResponse initializer, response() method will return dictionary
    return ajax.assign("#some-html-element-id", f"Received id: {id}").response()
```

## Development

First install `pre-commit`

```shell
$ pip install pre-commit
$ pre-commit install
```

### Publishing Python

```shell
$ python -m build
$ twine upload dist/*
```

### Publishing JS

In the `beeflow_ajax/beeflow_ajax_js` directory, run commands

```shell
$ npm version patch
$ npm publish
```

Then use these urls in the browser:
* https://cdn.jsdelivr.net/npm/@beeflow/beeflow_ajax_js@<correct_version>/css/BeeflowAjax.css
* https://cdn.jsdelivr.net/npm/@beeflow/beeflow_ajax_js@<correct_version>/js/js-url-2.3.0.min.js
* https://cdn.jsdelivr.net/npm/@beeflow/beeflow_ajax_js<correct_version>/js/BeeflowAjax.js
* https://cdn.jsdelivr.net/npm/@beeflow/beeflow_ajax_js@<correct_version>/js/BeeflowAjaxSwalMessages.js
