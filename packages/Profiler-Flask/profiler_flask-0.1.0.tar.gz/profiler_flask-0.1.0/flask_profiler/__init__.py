import functools
import logging
import re
import time
import typing as tp
from collections.abc import Mapping
from pprint import pprint as pp

from flask import (
    Blueprint,
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    url_for,
)
from flask_httpauth import HTTPBasicAuth

from . import storage

Config = Mapping[str, tp.Any]
Context = Mapping[str, str | Mapping[str, tp.Any]]

config: Config
collection: storage.BaseStorage


class AnyCallable(tp.Protocol):
    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> tp.Any: ...


auth = HTTPBasicAuth()
logger = logging.getLogger("profiler")


@auth.verify_password
def verify_password(username: str, password: str) -> bool:
    if "basicAuth" not in config or not config["basicAuth"]["enabled"]:
        return True

    basicAuth = config["basicAuth"]
    if username == basicAuth["username"] and password == basicAuth["password"]:
        return True

    logging.warn("Profiler-Flask authentication failed")
    return False


class Measurement:
    """Represents an endpoint measurement"""

    DECIMAL_PLACES = 6

    def __init__(
        self: tp.Self,
        name: str,
        args: tp.Any,
        kwargs: tp.Any,
        method: str,
        context: Context | None = None,
    ) -> None:
        super().__init__()
        self.context = context
        self.name = name
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.startedAt = 0
        self.endedAt = 0
        self.elapsed = 0

    def __json__(self: tp.Self) -> dict[str, tp.Any]:
        return {
            "name": self.name,
            "args": self.args,
            "kwargs": self.kwargs,
            "method": self.method,
            "startedAt": self.startedAt,
            "endedAt": self.endedAt,
            "elapsed": self.elapsed,
            "context": self.context,
        }

    def __str__(self: tp.Self) -> str:
        return str(self.__json__())

    def start(self: tp.Self) -> None:
        # we use default_timer to get the best clock available.
        # see: http://stackoverflow.com/a/25823885/672798
        self.startedAt = time.time()

    def stop(self: tp.Self) -> None:
        self.endedAt = time.time()
        self.elapsed = round(self.endedAt - self.startedAt, self.DECIMAL_PLACES)


def is_ignored(name: str, conf: Config) -> bool:
    """ """
    ignore_patterns: list[str | None] = conf.get("ignore", [])
    for pattern in ignore_patterns:
        if re.search(pattern, name):
            return True
    return False


def measure(
    f: AnyCallable, name: str, method: str, context: Context | None = None
) -> AnyCallable:
    logger.debug(f"{name} is being processed.")
    if is_ignored(name, config):
        logger.debug(f"{name} is ignored.")
        return f

    @functools.wraps(f)
    def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
        if "sampling_function" in config and not callable(config["sampling_function"]):
            raise Exception(
                "If sampling_function is provided to profiler-flask via config, "
                "it must be callable, refer to: "
                "https://github.com/Dumbliidore/profiler-flask#sampling"
            )

        if "sampling_function" in config and not config["sampling_function"]():
            return f(*args, **kwargs)

        measurement = Measurement(name, args, kwargs, method, context)
        measurement.start()

        try:
            returnVal = f(*args, **kwargs)
        except Exception:
            raise
        finally:
            measurement.stop()
            if config.get("verbose", False):
                pp(measurement.__json__())
            collection.insert(measurement.__json__())

        return returnVal

    return wrapper


# filtering 界面modal数据展示
def wrap_http_endpoint(f: AnyCallable) -> AnyCallable:
    @functools.wraps(f)
    def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
        headers: Mapping[str, str] = {
            "Host": request.headers.get("Host", ""),
            "Referer": request.headers.get("Referer", ""),
            "User-Agent": request.headers.get("User-Agent", ""),
            "Connection": request.headers.get("Connection", ""),
            "Accept": request.headers.get("Accept", ""),
            "Accept-Encoding": request.headers.get("Accept-Encoding", ""),
            "Accept-Language": request.headers.get("Accept-Language", ""),
        }

        context: Context = {
            "url": request.base_url,
            "args": dict(request.args.items()) or "{ }",
            "form": dict(request.form.items()) or "{ }",
            "body": request.data.decode("utf-8", "strict") or "",
            "headers": headers,
            "func": request.endpoint or "",
            "ip": request.remote_addr or "",
        }
        endpoint_name = str(request.url_rule)
        wrapped = measure(f, endpoint_name, request.method, context)
        return wrapped(*args, **kwargs)

    return wrapper


def wrap_app_endpoints(app: Flask) -> None:
    """
    Wraps all endpoints defined in the given flask app to measure how long time
    each endpoints takes while being executed. This wrapping process is
    supposed not to change endpoint behavior.
    """
    for endpoint, func in app.view_functions.items():
        app.view_functions[endpoint] = wrap_http_endpoint(func)


def profile() -> tp.Callable | tp.NoReturn:
    """
    HTTP endpoint decorator
    """
    if not config:
        raise Exception("Before measuring anything, you need to call init_app()")

    def wrapper(f: tp.Callable) -> tp.Callable:
        return wrap_http_endpoint(f)

    return wrapper


def register_internal_routers(app: Flask) -> None:
    """
    These are the endpoints which are used to display measurements in the
    profiler-flask dashboard.

    Note: these should be defined after wrapping user defined endpoints
    via wrapAppEndpoints()
    """
    url_path = config.get("endpointRoot", "profiler")

    bp = Blueprint(
        "profiler",
        __name__,
        url_prefix="/" + url_path,
        static_folder="static",
        static_url_path="/static",
        template_folder="templates",
    )

    # 图表展示页
    @bp.route("/dashboard", methods=["GET"])
    @auth.login_required
    def dashboard():
        return render_template("dashboard.html", active="dashboard")

    # 请求筛选页
    @bp.route("/filtering", methods=["GET"])
    @auth.login_required
    def filtering():
        measurements = collection.filter()
        return render_template("filtering.html", data=measurements, active="filtering")

    # 设置页
    @bp.route("/settings", methods=["GET"])
    @auth.login_required
    def settings():
        return render_template("settings.html", active="settings")

    @bp.route("/data", methods=["GET"])
    @auth.login_required
    def get_data_within_days():
        days = int(request.args.get("days", 1))
        data = collection.filter_by_days(days)

        html = f"""
            <div id="draw" x-show="false" x-init="updatePage({ data })">
            </div>
        """
        return html

    # 下载数据库里的所有请求数据
    @bp.route("/db/data/download", methods=["GET"])
    @auth.login_required
    def download():
        response = jsonify({})
        response.headers["HX-Redirect"] = url_for("profiler.get_data_from_db")
        return response

    @bp.route("/db/data", methods=["GET"])
    @auth.login_required
    def get_data_from_db():
        response = jsonify({"summary": collection.get_summary()})
        response.headers["Content-Disposition"] = "attachment; filename=dump.json"
        response.headers["Content-Type"] = "application/json"
        return response

    # 删除数据库并弹出消息提示
    @bp.route("/db/data/delete", methods=["GET"])
    @auth.login_required
    def delete():
        text = "All database data removed successfully."

        if not collection.truncate():
            text = "Some error occurred while deleting database data."

        html = f"""
        <div class="pl-10 pb-[10px]">
            <div class="text-[16px]">
                {text}
            </div>
        </div>
        """

        return html

    @bp.after_request
    def x_robots_tag_header(response: Response):
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response

    app.register_blueprint(bp)


def init_app(app: Flask) -> tp.NoReturn | None:
    global collection, config

    config = app.config.get("profiler") or app.config.get("PROFILER")
    if not config:
        raise Exception(
            "To init profiler-flask, provide "
            "required config through flask app's config. please refer: "
            "https://github.com/Dumbliidore/profiler-flask"
        )

    # 判断 flask 是否处于 DEBUG 模式
    if not app.config.get("DEBUG", True):
        raise Exception("Not DEBUG, please set app.config[DEBUG] = True.")

    collection = storage.get_collection(config.get("storage", {}))

    wrap_app_endpoints(app)
    register_internal_routers(app)

    basicAuth: Mapping[str, Mapping[str, bool | str]] = config.get("basicAuth")
    if not basicAuth or not basicAuth.get("enabled", False):
        logging.warn(" * CAUTION: profiler-flask is working without basic auth!")


class Profiler:
    """Wrapper for extension."""

    def __init__(self: tp.Self, app: Flask | None = None) -> None:
        self._init_app = init_app
        if app:
            self.init_app(app)

    def init_app(self: tp.Self, app: Flask) -> None:
        init = functools.partial(self._init_app, app)
        app.before_first_request(init)
