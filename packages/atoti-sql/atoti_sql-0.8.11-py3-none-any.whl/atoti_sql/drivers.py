"""Supported drivers.

To use another JDBC driver, add the driver's JAR to :func:`atoti.Session`'s *extra_jars* parameter.

For instance JARs to connect to Google BigQuery can be found on `BigQuery documentation <https://cloud.google.com/bigquery/docs/reference/odbc-jdbc-drivers>`_.
Once added to the extra JARs, ``driver="com.simba.googlebigquery.jdbc.Driver"`` can be used.
"""

H2 = "org.h2.Driver"
"""H2 driver."""

IBM_DB2 = "com.ibm.db2.jcc.DB2Driver"
"""IBM DB2 driver."""

MARIADB = "org.mariadb.jdbc.Driver"
"""MariaDB driver."""

MYSQL = "com.mysql.cj.jdbc.Driver"
"""MySQL driver."""

ORACLE = "oracle.jdbc.OracleDriver"
"""Oracle driver."""

POSTGRESQL = "org.postgresql.Driver"
"""PostgreSQL driver."""

MICROSOFT_SQL_SERVER = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
"""Microsoft SQL Server driver."""
