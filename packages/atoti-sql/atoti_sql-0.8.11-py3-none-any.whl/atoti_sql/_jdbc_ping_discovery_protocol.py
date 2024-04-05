from dataclasses import dataclass
from textwrap import dedent

from atoti.experimental._distributed import DiscoveryProtocol
from atoti_core import keyword_only_dataclass
from typing_extensions import override


def _bool_to_xml(value: bool, /) -> str:  # noqa: FBT001
    return str(value).lower()


@keyword_only_dataclass
@dataclass(frozen=True)
class JDBCPingDiscoveryProtocol(DiscoveryProtocol):
    connection_url: str
    connection_username: str
    connection_password: str
    connection_driver: str
    """JDBC driver class name. See :mod:`atoti_sql.drivers` for supported drivers."""
    remove_all_data_on_view_change: bool = True
    """"Defined by the FILE_PING protocol. See http://jgroups.org/manual4/index.html#_removal_of_zombie_files"""
    remove_old_coords_on_view_change: bool = True
    """"Defined by the FILE_PING protocol. See http://jgroups.org/manual4/index.html#_removal_of_zombie_files"""
    write_data_on_find: bool = True
    """"Defined by the FILE_PING protocol. See http://jgroups.org/manual4/index.html#_removal_of_zombie_files"""

    @property
    @override
    def _xml(self) -> str:
        return dedent(
            f"""\
            <JDBC_PING
              connection_url="{self.connection_url}"
              connection_username="{self.connection_username}"
              connection_password="{self.connection_password}"
              connection_driver="{self.connection_driver}"
              remove_all_data_on_view_change="{_bool_to_xml(self.remove_all_data_on_view_change)}"
              remove_old_coords_on_view_change="{_bool_to_xml(self.remove_old_coords_on_view_change)}"
              write_data_on_find="{_bool_to_xml(self.write_data_on_find)}"
            />
            """
        )
