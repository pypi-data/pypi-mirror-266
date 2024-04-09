import json
import sqlite3
import typing as tp
from collections.abc import Iterator, Mapping, Sequence

from .base import BaseStorage


class Sqlite(BaseStorage):
    """Docstring for Sqlite"""

    def __init__(self: tp.Self, db_config: Mapping[str, tp.Any] | None = None) -> None:
        super().__init__()
        self.config = db_config
        self.sqlite_file: str = self.config.get("FILE", "flask_profiler.sql")
        self.table_name: str = self.config.get("TABLE", "measurements")

        self.startedAt = "startedAt"  # name of the column
        self.endedAt = "endedAt"  # name of the column
        self.elapsed = "elapsed"  # name of the column
        self.method = "method"
        self.args = "args"
        self.kwargs = "kwargs"
        self.name = "name"
        self.context = "context"

        self.connection = sqlite3.connect(self.sqlite_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        try:
            self.create_database()
        except sqlite3.OperationalError as e:
            if "already exists" not in str(e):
                raise e

    def __enter__(self) -> tp.Self:
        return self

    def create_database(self: tp.Self) -> None:
        sql = f"""CREATE TABLE {self.table_name}
            (
            ID Integer PRIMARY KEY AUTOINCREMENT,
            {self.startedAt} REAL,
            {self.endedAt} REAL,
            {self.elapsed} REAL,
            {self.args} TEXT,
            {self.kwargs} TEXT,
            {self.method} TEXT,
            {self.context} TEXT,
            {self.name} TEXT
            );
        """
        self.cursor.execute(sql)

        sql = f"""
        CREATE INDEX measurement_index ON {self.table_name}
            ({self.startedAt}, {self.endedAt}, {self.elapsed}, {self.name}, {self.method});
        """
        self.cursor.execute(sql)
        self.connection.commit()

    def insert(self: tp.Self, kwds: Mapping[str, tp.Any]) -> None:
        endedAt = float(kwds.get("endedAt", None))
        startedAt = float(kwds.get("startedAt", None))
        elapsed = kwds.get("elapsed", None)
        args = json.dumps(list(kwds.get("args", ())))  # tuple -> list -> json
        kwargs = json.dumps(kwds.get("kwargs", ()))
        context = json.dumps(kwds.get("context", {}))
        method = kwds.get("method", None)
        name = kwds.get("name", None)

        sql = f"""INSERT INTO {self.table_name} VALUES (
            null, ?, ?, ?, ?,?, ?, ?, ?)"""

        self.cursor.execute(
            sql, (startedAt, endedAt, elapsed, args, kwargs, method, context, name)
        )

        self.connection.commit()

    def filter(self: tp.Self) -> Iterator[dict[str, tp.Any]]:
        sql = f"""
                SELECT 
                    method, name,
                    elapsed, context, 
                    strftime(
                        '%Y-%m-%d',
                        datetime(startedAt, 'unixepoch', 'localtime')
                    ) AS date
                FROM "{self.table_name}"
                ORDER BY
                    date DESC
                """

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return (self.jsonify_row(row) for row in rows)

    def truncate(self: tp.Self) -> bool:
        self.cursor.execute(f"DELETE FROM {self.table_name}")
        self.connection.commit()
        # Making the api match with mongo collection, this function must return
        # True or False based on success of this delete operation
        return True if self.cursor.rowcount else False

    def delete(self: tp.Self, measurementId: int) -> None:
        self.cursor.execute(f'DELETE FROM "{self.table_name}" WHERE ID={measurementId}')
        return self.connection.commit()

    def jsonify_row(self, row: Sequence[tp.Any]) -> dict[str, tp.Any]:
        data = {
            "method": row[0],
            "name": row[1],
            "elapsed": row[2],
            "context": json.loads(row[3]),
            "startedAt": row[4],
        }

        return data

    # 获取所有请求的汇总数据
    def get_summary(self: tp.Self) -> list[tp.Any]:
        sql = f"""
            SELECT
                method, name,
                count(id) as count,
                min(elapsed) as minElapsed,
                max(elapsed) as maxElapsed,
                avg(elapsed) as avgElapsed,
                startedAt as timestamp
            FROM 
                "{self.table_name}"
            GROUP BY
                method, name
            """

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        result = []
        for i, r in enumerate(rows, 1):
            result.append(
                {
                    "id": i,
                    "method": r[0],
                    "name": r[1],
                    "count": r[2],
                    "minElapsed": r[3],
                    "maxElapsed": r[4],
                    "avgElapsed": r[5],
                    "timestamp": r[6],
                }
            )

        return result

    def filter_by_days(self: tp.Self, days: int = 1) -> list[tp.Any]:
        time_format = "'%m-%d %H'"
        if days != 1:
            time_format = "'%m-%d'"

        sql = f"""
        SELECT
            method, name,
            count(method) as count,
            min(elapsed) as minElapsed,
            max(elapsed) as maxElapsed,
            avg(elapsed) as avgElapsed,
            strftime(
                        {time_format},
                        datetime(startedAt, 'unixepoch', 'localtime')
            ) AS day
        FROM
            "{self.table_name}"
        WHERE
            startedAt >= strftime('%s', 'now', '-{days} days')
        GROUP BY
            method, name, day
        ORDER BY
            day ASC;
        """

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        days_data = []
        for i, r in enumerate(rows, 1):
            days_data.append(
                {
                    "index": i,
                    "method": r[0],
                    "name": r[1],
                    "count": r[2],
                    "minElapsed": r[3],
                    "maxElapsed": r[4],
                    "avgElapsed": r[5],
                    "day": r[6],
                }
            )

        return days_data

    def __exit__(self: tp.Self, exc_type, exc_value, traceback) -> None:
        return self.connection.close()
