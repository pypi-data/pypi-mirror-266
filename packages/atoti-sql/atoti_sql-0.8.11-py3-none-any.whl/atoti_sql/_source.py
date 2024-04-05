from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet
from typing import Optional

import atoti as tt
from atoti._java_api import JavaApi
from atoti._jdbc_utils import normalize_jdbc_url
from atoti._sources.data_source import DataSource, InferTypes, LoadDataIntoTable
from atoti_core import Constant, ConstantValue, TableIdentifier
from typing_extensions import override

from ._infer_driver import infer_driver


def _create_source_params(
    *,
    driver: str,
    sql: str,
    url: str,
) -> dict[str, object]:
    return {
        "driverClass": driver,
        "query": sql,
        "url": url,
    }


class SqlDataSource(DataSource):
    def __init__(
        self, *, infer_types: InferTypes, load_data_into_table: LoadDataIntoTable
    ) -> None:
        super().__init__(load_data_into_table=load_data_into_table)

        self._infer_types = infer_types

    @property
    @override
    def key(self) -> str:
        return "JDBC"

    def load_sql_into_table(
        self,
        identifier: TableIdentifier,
        sql: str,
        /,
        *,
        driver: str,
        scenario_name: str,
        url: str,
    ) -> None:
        source_params = _create_source_params(
            driver=driver,
            sql=sql,
            url=url,
        )
        self.load_data_into_table(
            identifier,
            source_params,
            scenario_name=scenario_name,
        )

    def infer_sql_types(
        self,
        sql: str,
        /,
        *,
        keys: AbstractSet[str],
        default_values: Mapping[str, Optional[Constant]],
        url: str,
        driver: str,
    ) -> dict[str, tt.DataType]:
        source_params = _create_source_params(
            driver=driver,
            sql=sql,
            url=url,
        )
        return self._infer_types(
            self.key,
            source_params,
            keys=keys,
            default_values=default_values,
        )


def infer_sql_types(
    sql: str,
    /,
    *,
    url: str,
    driver: Optional[str] = None,
    keys: AbstractSet[str],
    default_values: Mapping[str, Optional[ConstantValue]],
    java_api: JavaApi,
) -> dict[str, tt.DataType]:
    url = normalize_jdbc_url(url)
    return SqlDataSource(
        load_data_into_table=java_api.load_data_into_table,
        infer_types=java_api.infer_table_types_from_source,
    ).infer_sql_types(
        sql,
        keys=keys,
        default_values={
            column_name: None if value is None else Constant(value)
            for column_name, value in default_values.items()
        },
        url=url,
        driver=driver or infer_driver(url),
    )


def load_sql(
    identifier: TableIdentifier,
    sql: str,
    /,
    *,
    url: str,
    driver: Optional[str] = None,
    java_api: JavaApi,
    scenario_name: str,
) -> None:
    url = normalize_jdbc_url(url)
    SqlDataSource(
        load_data_into_table=java_api.load_data_into_table,
        infer_types=java_api.infer_table_types_from_source,
    ).load_sql_into_table(
        identifier,
        sql,
        driver=driver or infer_driver(url),
        scenario_name=scenario_name,
        url=url,
    )
