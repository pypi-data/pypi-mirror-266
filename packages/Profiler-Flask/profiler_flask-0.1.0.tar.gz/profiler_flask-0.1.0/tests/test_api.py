import pytest
from base import app
from flask.testing import FlaskClient


@pytest.fixture()
def client():
    with app.test_client() as client:
        yield client


def test_route_with_profiler(client: FlaskClient):
    client.get("/profiler/db/data/delete", auth=("admin", "admin"))
    res = client.get("/product/1")

    content = res.get_data(as_text=True)
    assert content == "product id is 1"
    assert res.status_code == 200

    res = client.get("/profiler/db/data", auth=("admin", "admin"))
    content = res.get_json()
    method = content["summary"][0]["method"]
    name = content["summary"][0]["name"]
    count = content["summary"][0]["count"]
    assert count == 1
    assert method == "GET"
    assert name == "/product/<id>"
    assert res.status_code == 200


def test_route_no_profiler(client: FlaskClient):
    client.get("/profiler/db/data/delete", auth=("admin", "admin"))
    res = client.get("/doSomething")

    content = res.get_data(as_text=True)
    assert content == "profiler will not measure this."
    assert res.status_code == 200

    res = client.get("/profiler/db/data", auth=("admin", "admin"))
    content = res.get_json()
    assert content == {"summary": []}
    assert res.status_code == 200


def test_route_with_profiler_decorator(client: FlaskClient):
    client.get("/profiler/db/data/delete", auth=("admin", "admin"))
    res = client.get("/doSomethingImportant/1")

    content = res.get_data(as_text=True)
    assert content == "profiler will measure this request."
    assert res.status_code == 200

    res = client.get("/profiler/db/data", auth=("admin", "admin"))
    content = res.get_json()
    method = content["summary"][0]["method"]
    name = content["summary"][0]["name"]
    count = content["summary"][0]["count"]
    assert count == 1
    assert method == "GET"
    assert name == "/doSomethingImportant/<id>"
    assert res.status_code == 200


def test_get_data_within_days(client: FlaskClient):
    client.get(
        "/profiler/db/data/delete",
        auth=("admin", "admin"),
    )
    client.get("/product/1")
    res = client.get("/profiler/data?days=1", auth=("admin", "admin"))

    content = res.get_data(as_text=True)
    method = "GET"
    name = "product/<id>"
    count = 1

    assert method in content
    assert name in content
    assert str(count) in content
    assert res.status_code == 200


def test_download(client: FlaskClient):
    res = client.get(
        "/profiler//db/data/download", auth=("admin", "admin"), follow_redirects=True
    )
    assert res.request.path == "/profiler/db/data/download"
    assert res.headers["HX-Redirect"] == "/profiler/db/data"
    assert len(res.history) == 1
    assert res.status_code == 200


def test_delete(client: FlaskClient):
    client.get("/product/1")

    html = """
        <div class="pl-10 pb-[10px]">
            <div class="text-[16px]">
                All database data removed successfully.
            </div>
        </div>
        """
    res = client.get("/profiler/db/data/delete", auth=("admin", "admin"))
    content = res.get_data(as_text=True)
    assert content == html
    assert res.status_code == 200

    error_html = """
        <div class="pl-10 pb-[10px]">
            <div class="text-[16px]">
                Some error occurred while deleting database data.
            </div>
        </div>
        """

    res = client.get("/profiler/db/data/delete", auth=("admin", "admin"))
    content = res.get_data(as_text=True)

    assert content == error_html
    assert res.status_code == 200
