"""Plugin to load the results of SQL queries into Atoti tables.

This package is required to use :meth:`atoti.Table.load_sql` and :meth:`atoti.Session.read_sql`.

Supported SQL implementations are the ones available in :mod:`atoti_sql.drivers`.

"""

from ._jdbc_ping_discovery_protocol import (
    JDBCPingDiscoveryProtocol as JDBCPingDiscoveryProtocol,
)
