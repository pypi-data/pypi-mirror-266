import importlib
import os
import sys
import typing as tp
from collections.abc import Mapping
from contextlib import contextmanager

from .base import BaseStorage


@contextmanager
def cwd_in_path():
    """将项目路径添加到全局，检索数据库驱动"""
    cwd = os.getcwd()
    if cwd in sys.path:
        yield
    else:
        sys.path.insert(0, cwd)
        try:
            yield
        finally:
            sys.path.remove(cwd)


def get_collection(db_config: Mapping[str, tp.Any]) -> BaseStorage:
    engine: str = db_config.get("engine", "")
    if engine.lower() == "mongodb":
        from .mongo import Mongo

        return Mongo(db_config)
    elif engine.lower() == "sqlite":
        from .sqlite import Sqlite

        return Sqlite(db_config)
    elif engine.lower() == "sqlalchemy":
        from .sql_alchemy import Sqlalchemy

        return Sqlalchemy(db_config)
    else:
        try:
            parts = engine.split(".")
            if len(parts) < 1:  # engine must have at least module name and class
                raise ImportError

            module_name = ".".join(parts[:-1])
            class_name = parts[-1]

            # we need to make sure that it will be able to find module in your
            # project directory
            with cwd_in_path():
                module = importlib.import_module(module_name)

            storage = getattr(module, class_name)
            if not issubclass(storage, BaseStorage):
                raise ImportError(
                    f"{class_name.title()} isn't supported, please use `mongo`, `sqlite` or `sqlalchemy`"
                )

        except ImportError:
            raise ValueError(
                (
                    "Profiler-Flask requires a valid storage engine but it is"
                    f" missing or wrong. provided engine: {engine}"
                )
            )

        return storage(db_config)
