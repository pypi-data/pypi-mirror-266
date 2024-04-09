from flask import Flask

import flask_profiler

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["TESTING"] = True
app.config["profiler"] = {
    "storage": {"engine": "sqlite", "FILE": "test.sql"},
    "basicAuth": {"enabled": True, "username": "admin", "password": "admin"},
    "ignore": ["^/static/.*"],
}


@app.route("/product/<id>", methods=["GET"])
def getProduct(id):
    return "product id is " + str(id)


@app.route("/product/<id>", methods=["PUT"])
def updateProduct(id):
    return "product {} is being updated".format(id)


@app.route("/products", methods=["GET"])
def listProducts():
    return "suppose I send you product list..."


flask_profiler.init_app(app)


@app.route("/doSomething", methods=["GET"])
def doSomething():
    return "profiler will not measure this."


@app.route("/doSomethingImportant/<id>", methods=["GET"])
@flask_profiler.profile()
def doSomethingImportant(id):
    return "profiler will measure this request."
