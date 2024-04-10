# Naja Atra WSGI

This ia a WSGI proxy that proxies requests to Naja Atra.

# Usage

```python
from naja_atra import route
from naja_atra_wsgi import app
from wsgiref.simple_server import make_server

@route("/hello")
def hello(name: str):
    return {"messag": f"Hello, {name}!"}

if __name__ == '__main__':
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

```

You can use `server.scan()` to import routes from other modules. And also you can use `naja_atra_wsgi.config()` to function to sepecify the static resources routes.

```python
import os
import naja_atra.server as server

from wsgiref.simple_server import make_server
from naja_atra_wsgi import config, app

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    
    server.scan(base_dir="tests/ctrls", regx=r'.*controllers.*')
    config(resources={"/public/*": f"{PROJECT_ROOT}/tests/static",
                    "/*": f"{PROJECT_ROOT}/tests/static"})

    wsgi_server = make_server("", 9090, app)
    wsgi_server.serve_forever()
```
