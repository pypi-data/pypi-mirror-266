## Intruduction
**Profiler-Flask comes from the refactoring of flask-profiler, and I would like to express my heartfelt thanks to its author [@muatik](https://github.com/muatik) for his open source spirit and excellent code.**

The project beautifies the front-end interface on the basis of flask-profiler, and is basically consistent with its function.

With the web interface, You can monitor all your endpoints' performance you want to monitor and check the performance of endpoints and requests through filters.

## Screenshots

Dashboard view

![image](https://github.com/Dumbliidore/profiler-flask/blob/main/assets/dashboard.png)


You can create filters to investigate certain type requests.

![image](https://github.com/Dumbliidore/profiler-flask/blob/main/assets/filtering.png)


You can see all the details of a request.

![image](https://github.com/Dumbliidore/profiler-flask/blob/main/assets/details.png)



## Installation
use `pdm`
```powershell
pdm add profiler-flask
```
use `pip`
```
pip install profiler-flask
```


## Example
This is an example. Let's dive in.

```python
from flask import Flask
import flask_profiler


app = Flask(__name__)
app.config["DEBUG"] = True
app.config["profiler"] = {
    "storage": {"engine": "sqlite"},
    "basicAuth": {"enabled": True, "username": "admin", "password": "admin"},
    "ignore": ["^/static/.*"],
}

@app.route("/product/<id>", methods=["GET"])
def getProduct(id):
    return f"product id is {id}"


@app.route("/product/<id>", methods=["PUT"])
def updateProduct(id):
    return f"product {id} is being updated"


@app.route("/products", methods=["GET"])
def listProducts():
    return "suppose I send you product list..."

flask_profiler.init_app(app)

# 也可以使用装饰器的方法使用
@app.route("/doSomethingImportant/<id>", methods=["GET"])
@flask_profiler.profile()
def doSomethingImportant(id):
    return "profiler will measure this request."
```

Now, run your flask app.

## Using with different database system
You can use profiler-flask with Sqlite database systems.

#### SQLite
In order to use SQLite, just specify it as the value of storage.engine directive as follows.

```python
app.config["profiler"] = {
    "storage": {
        "engine": "sqlite",
    }
}
```

Below the other options are listed.
|  Filter key   |                  Description                  |      Default       |
| :-----------: | :-------------------------------------------: | :----------------: |
| storage.FILE  |           SQLite database file name           | flask_profiler.sql |
| storage.TABLE | table name in which profiler data will reside |    measurements    |

## Sampling
Control the number of samples taken by profiler-flask

You would want control over how many times should the profiler-flask take samples while running in production mode. You can supply a function and control the sampling according to your business logic.

Example 1: Sample 1 in 100 times with random numbers

```python
app.config["profiler"] = {
    "sampling_function": lambda: True if random.sample(list(range(1, 101)), 1) == [42] else False
}
```

Example 2: Sample for specific users

```python
app.config["profiler"] = {
    "sampling_function": lambda: True if user is 'Dumblidore' else False
}
```

If sampling function is not present, all requests will be sampled.

### Changing profiler-flask endpoint root
By default, we can access profiler-flask at /profiler, but you can change the endpoint root.

Example:
```python
app.config["profiler"] = {
        "endpointRoot": "profiler-flask"
}
```
the endpoint root will be changed to /profiler-flask.

### Ignored endpoints

Profiler-Flask will try to track every endpoint defined so far when init_app() is invoked. If you want to exclude some of the endpoints, you can define matching regex for them as follows:

```python
app.config["profiler"] = {
        "ignore": [
	        "^/static/.*",
	        "/api/users/\w+/password"
        ]
}
```


## License
This project is licensed under the MIT License (see the `LICENSE` file for details). Some macros were part of Flask-Profiler and were modified under the terms of its MIT License.
