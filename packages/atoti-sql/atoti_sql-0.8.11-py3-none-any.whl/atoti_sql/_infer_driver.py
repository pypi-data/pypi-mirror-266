import re

from atoti._jdbc_utils import _JDBC_PREFIX

from .drivers import (
    H2,
    IBM_DB2,
    MARIADB,
    MICROSOFT_SQL_SERVER,
    MYSQL,
    ORACLE,
    POSTGRESQL,
)

_DRIVER_PER_PATH = {
    "db2": IBM_DB2,
    "h2": H2,
    "mariadb": MARIADB,
    "mysql": MYSQL,
    "oracle": ORACLE,
    "postgresql": POSTGRESQL,
    "sqlserver": MICROSOFT_SQL_SERVER,
}

_DRIVER_PATH_PATTERN = f"{_JDBC_PREFIX}(?P<driver>[^:]+):"


def infer_driver(url: str) -> str:
    match = re.match(_DRIVER_PATH_PATTERN, url)

    if match:
        driver = match.group("driver")

        if driver in _DRIVER_PER_PATH:
            return _DRIVER_PER_PATH[driver]

    raise ValueError(f"Cannot infer driver from URL: {url}")
