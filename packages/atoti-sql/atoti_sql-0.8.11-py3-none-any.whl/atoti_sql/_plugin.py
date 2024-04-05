from pathlib import Path
from typing import Optional

import atoti as tt
from atoti_core import BaseSessionBound, Plugin
from typing_extensions import override

from ._source import infer_sql_types, load_sql


class SqlPlugin(Plugin):
    @property
    @override
    def jar_path(self) -> Optional[Path]:
        return Path(__file__).parent / "data" / "atoti-sql.jar"

    @property
    @override
    def java_package_name(self) -> Optional[str]:
        return "io.atoti.loading.sql"

    @override
    def post_init_session(self, session: BaseSessionBound, /) -> None:
        if not isinstance(session, tt.Session):
            return

        session._infer_sql_types = infer_sql_types
        session._load_sql = load_sql
