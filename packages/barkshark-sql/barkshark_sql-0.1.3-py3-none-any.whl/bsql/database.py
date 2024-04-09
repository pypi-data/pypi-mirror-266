from __future__ import annotations

import queue
import typing

from contextlib import contextmanager
from getpass import getuser
from pathlib import Path
from uuid import uuid4

from .backends import Backend
from .misc import ColumnDescription, Row, StatementParsingError
from .statement import Statement, Select, Insert, Update, Delete
from .table import Tables

if typing.TYPE_CHECKING:
	from collections.abc import Generator, Iterable, Iterator
	from types import TracebackType
	from typing import Any
	from .enums import BackendType
	from .misc import ConnectionProto, CursorProto

	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


TRANS_QUERIES = (
	"alter",
	"begin",
	"create",
	"delete",
	"drop",
	"insert",
	"replace",
	"update",
	"upsert"
)


class Connection:
	"Represents a database connection"

	def __init__(self, database: Database, start_trans: bool = False):
		"""
			Create a new database connection

			:param database: Database object to get the config from to open the connection
			:param start_trans: Whether or not to start a transaction when using the connection
				as a context manager
		"""

		self.id = uuid4()
		"Unique ID of the connection"

		self.database: Database = database
		"Database the connection is associated with"

		self._start_trans = start_trans
		self._conn: ConnectionProto | None = database.backend.get_connection(database)
		self._trans = False


	def __enter__(self) -> Connection:
		self.connect()

		if self._start_trans:
			self.begin()

		return self


	def __exit__(self, etype: type[Exception], evalue: Exception, tb: TracebackType) -> None:
		if self._start_trans:
			if not tb or evalue:
				self.commit()

			else:
				self.rollback()

		self.disconnect()


	@property
	def connected(self) -> bool:
		"Whether or not the connection is active"

		return self._conn is not None


	@property
	def in_transaction(self) -> bool:
		"Whether or not a transaction is active"

		return self._trans


	@contextmanager
	def transaction(self) -> Generator[None, None, None]:
		"Start and end a transaction with a context manager."

		self.begin()

		try:
			yield
			self.commit()

		except Exception as e:
			self.rollback()
			raise e


	def connect(self) -> None:
		if self._conn:
			return

		self._conn = self.database.backend.get_connection(self.database)


	def disconnect(self) -> None:
		"Close the connection"

		if self._conn is None:
			return

		self._conn.close()
		self._conn = None


	def begin(self) -> None:
		"Start a new transaction if one is not active."

		if self._conn is None:
			raise ConnectionError("Connection closed")

		if self.in_transaction:
			return

		with self.execute("BEGIN"):
			pass


	def commit(self) -> None:
		"Commit any changed data to the database and end the transaction if one is active."

		if self._conn is None:
			raise ConnectionError("Connection closed")

		with self.execute("COMMIT"):
			pass


	def rollback(self) -> None:
		"Discard any changed data and end the transaction if one is active."

		if self._conn is None:
			raise ConnectionError("Connection closed")

		with self.execute("ROLLBACK"):
			pass


	def cursor(self) -> Cursor:
		"Create a new cursor object."

		if self._conn is None:
			raise ConnectionError("Connection closed")

		return Cursor(self, self._conn.cursor())


	def execute(self, query: str, params: dict[str, Any] | None = None) -> Cursor:
		"""
			Execute an SQL query. Placeholders use the ``:{name}`` convention.

			:param query: SQL statement to be executed
			:param params: Parameters to be used when replacing the placeholders in the query
		"""

		cursor = self.cursor()
		cursor.execute(query, params)
		return cursor


	def query(self, statement: Statement) -> Cursor:
		"""
			Execute a ``Statement`` object

			:param statement: ``Statement`` object to be executed
		"""

		cursor = self.cursor()
		cursor.query(statement)
		return cursor


	def run(self, name: str, params: dict[str, Any] | None = None) -> Cursor:
		"""
			Execute a prepared statement

			:param name: Name of the prepared statement
			:param params: Parameters to be used when replacing the placeholders in the query
		"""

		cur = self.cursor()
		cur.run(name, params)
		return cur


	def get_databases(self) -> Iterable[str]:
		"Get the names of all the databases in the backend. Sqlite backends will return an empty tuple."

		return self.database.backend.get_databases(self)


	def get_tables(self) -> Iterable[str]:
		"Get the names of all the tables in the database."

		return self.database.backend.get_tables(self)


	def create_tables(self, tables: Tables | None = None) -> None:
		"""
			Create the tables for the database. If ``tables`` is ``None``, the tables in
			:attr:`Database.tables` will be used instead.

			:param tables: Tables to build into SQL queries and then execute
		"""

		if not tables:
			tables = self.database.tables

		for table in tables.values():
			with self.execute(table.build(self.database.backend_type)):
				pass


	# Convenience query methods

	def select(self,
				table: str,
				*order_by: str,
				limit: int = 0,
				offset: int = 0,
				**where: Any) -> Cursor:
		"""
			Execute a SELECT statement

			:param table: Database table to work with
			:param order_by: Columns to sort the rows by in ascending order
			:param limit: Maximum number of rows to return
			:param offset: Row index to start returning rows from
			:param where: Column and values to search by
		"""

		stmt = Select(table, limit = limit, offset = offset)

		for item in order_by:
			stmt.set_order_by(item, "ASC")

		for key, value in where.items():
			stmt.set_where(key, value)

		return self.query(stmt)


	def insert(self, table: str, data: dict[str, Any]) -> Cursor:
		"""
			Execute an INSERT statement

			:param table: Database table to work with
			:param data: Row data to insert
		"""

		return self.query(Insert(table, data))


	def update(self,
				table: str,
				data: dict[str, Any],
				limit: int = 0,
				offset: int = 0,
				**where: Any) -> Cursor:
		"""
			Execute an UPDATE statement

			:param table: Database table to work with
			:param data: Row data to insert
			:param limit: Maximum number of rows to return
			:param offset: Row index to start returning rows from
			:param where: Column and values to search by
		"""

		stmt = Update(table, data, limit, offset)

		for key, value in where.items():
			stmt.set_where(key, value)

		return self.query(stmt)


	def delete(self, table: str, limit: int = 0, offset: int = 0, **where: Any) -> Cursor:
		"""
			Execute a DELETE statement

			:param table: Database table to work with
			:param limit: Maximum number of rows to return
			:param offset: Row index to start returning rows from
			:param where: Column and values to search by
		"""

		stmt = Delete(table, limit, offset)

		for key, value in where.items():
			stmt.set_where(key, value)

		return self.query(stmt)


T = typing.TypeVar("T", bound = Connection)


class Database(typing.Generic[T]):
	"Manages a pool of database connections"

	def __init__(self,
				backend_name: str,
				database: str,
				host: str | Path = Path("/var/run/postgresql"),
				port: int = 5432,
				username: str = getuser(),
				password: str | None = None,
				connection_class: type[T] = Connection, # type: ignore
				pool_size: int = 5,
				pool_timeout: int = 5,
				tables: Tables | dict[str, Any] | str | None = None,
				prepared_statements: dict[str, str] | None = None,
				**kwargs: Any):
		"""
			Create a new ``Database`` object

			:param backend_name: Lowercase name of a class that sub-classes :class:`Backend`
			:param database: Database name (postgres) or path (sqlite)
			:param host: Address or unix socket for connecting to the server
			:param port: Port the server is listening on
			:param username: User to connect to the server with
			:param password: Password of the user
			:param connection_class: Connection class to use when creating new connections
			:param pool_size: Number of connections to open
			:param pool_timeout: Number of seconds to wait for an available connection from the
				connection pool
			:param tables: Table schema of the database
			:param prepared_statements: SQL queries that can be called with :meth:`Connection.run`
			:param kwargs: Arguments to pass to the backend connection function
		"""

		if connection_class is not None and not issubclass(connection_class, Connection):
			raise TypeError("Connection class must be a sub-class of 'Connection'")

		self.backend: Backend = Backend.get(backend_name)()
		"Backend to use for connections"

		self.database: str = database
		"Database name (postgres) or path (sqlite)"

		self.host: str | Path = host
		"Address or unix socket for connecting to the server"

		self.port: int = port
		"Port the server is listening on"

		self.username: str = username
		"User to connect to the server with"

		self.password: str | None = password
		"Password of the user"

		self.arguments: dict[str, Any] = kwargs
		"Arguments to pass to the backend connection function"

		self.connection_class: type[T] = connection_class
		"Connection class to use when creating new connections"

		self.pool_size: int = pool_size
		"Number of connections to connect"

		self.pool_timeout: int = pool_timeout
		"Number of seconds to wait for an available connection from the connection pool"

		self.prepared_statements: dict[str, str] = prepared_statements or {}
		"Saved SQL queries that can be called with :meth:`Connection.run`"

		self.tables: Tables = Tables()
		"Table layout for the database"

		if isinstance(tables, Tables):
			self.tables = tables

		elif isinstance(tables, (dict, str)):
			self.tables = Tables.from_json(tables)

		elif tables:
			raise TypeError("'tables' param must be a Tables, dict, or str object")

		self._pool: queue.SimpleQueue[T] = queue.SimpleQueue()
		self._connected: bool = False


	def __enter__(self) -> Self:
		self.connect()
		return self


	def __exit__(self, *_) -> None:
		self.disconnect()


	@classmethod
	def postgresql(cls: type[Database], *args: Any, **kwargs: Any) -> Database:
		"""
			Create a new ``Database`` object with the :class:`PG8000` backend.

			:param args: Positional arguments to pass to :class:`Database`
			:param kwargs: Keyword arguments to pass to :class:`Database`
		"""

		return cls("pg8000", *args, **kwargs)


	@classmethod
	def sqlite(cls: type[Database], path: str | Path, **kwargs: Any) -> Database:
		"""
			Create a new ``Database`` object with the :class:`PG8000` backend.

			:param path: Path to the database file
			:param kwargs: Keyword arguments to pass to :class:`Database`
		"""

		file_path = Path(path).expanduser().resolve()
		return cls("sqlite3", str(file_path), **kwargs)


	@property
	def backend_type(self) -> BackendType:
		return self.backend.backend_type


	@property
	def connected(self) -> bool:
		"Whether or not the database is connected to the backend"

		return self._connected


	# todo: split into public and private functions
	def add_prepared_statement(self,
								name: str,
								query: str | list[str],
								_start_index: int = 0) -> None:
		"""
			Add a new prepared statement

			:param name: Name of the statement
			:param query: Statement to be added
			:param _start_index: Used internally
		"""

		query_lines: list[str] = query.split("\n") if isinstance(query, str) else query
		end_statement: bool = False
		new_lines: list[str] = []

		for idx, line in enumerate(query_lines):
			if not line.strip():
				continue

			if ";" in line:
				if end_statement or line[line.index(";")] != line[-1]:
					raise StatementParsingError(
						"Cannot have multiple queries in a single statement",
						name, idx + _start_index, line.index(";")
					)

				end_statement = True

			new_lines.append(line.strip())

		if not end_statement:
			raise StatementParsingError(
				"Statement does not end with a semi-colon",
				name, len(new_lines) + _start_index, len(new_lines[-1])
			)

		self.prepared_statements[name] = " ".join(new_lines)


	def get_connection(self, start_trans: bool = False) -> T:
		"""
			Create a new connection without the pool.

			:param start_trans: Start a transaction
		"""

		return self.connection_class(self, start_trans)


	@contextmanager
	def session(self, start_trans: bool = False) -> Generator[T, None, None]:
		"""
			Fetch a connection from the pool.

			:param start_trans: Start a transaction on the connection
		"""

		if not self.connected:
			self.connect()

		try:
			conn = self._pool.get(block = True, timeout = self.pool_timeout)

			if start_trans:
				conn.begin()

			elif not conn.connected:
				conn.connect()

			yield conn

			if conn.in_transaction:
				conn.commit()

		except queue.Empty:
			raise RuntimeError("No available connections in the pool")

		except Exception as e:
			if conn and conn.in_transaction:
				conn.rollback()

			raise e

		finally:
			if self.connected:
				self._pool.put(conn)

			else:
				conn.disconnect()


	def connect(self) -> None:
		"Create connections up to the amount specified by :attr:`Database.pool_size`"

		if self.connected:
			return

		for _ in range(self.pool_size):
			self._pool.put(self.get_connection(False))

		self._connected = True


	def disconnect(self) -> None:
		"Close all pool connections"

		if not self.connected:
			return

		while True:
			try:
				conn = self._pool.get(block = False)
				conn.disconnect()

			except queue.Empty:
				break

		self._connected = False


	def load_prepared_statements(self, path: Path | str) -> None:
		"""
			Parse an SQL file with named functions

			:param path: Path to the SQL file
		"""
		if isinstance(path, str):
			path = Path(path).expanduser().resolve()

		with path.open("r", encoding = "utf-8") as fd:
			self.load_prepared_statements_from_string(fd.read())


	def load_prepared_statements_from_string(self, data: str) -> None:
		"""
			Parse a string with named SQL statements.

			Example: The code block below would add ``get-config`` and ``set-config`` named
			functions.

			.. code-block:: SQL

				-- name: get-config
				SELECT * FROM config WHERE key = :key;

				-- name: set-config
				INSERT INTO config (key, value, type)
				VALUES (:key, :value, :type)
				ON CONFLICT (key)
				DO UPDATE SET value = :value;

			:param data: String data to parse
			:raises StatementParsingError: When a statement cannot be parsed
		"""

		current_name: str = ""
		current_lines: list[str] = []
		statement_end: bool = False

		for idx, raw_line in enumerate(data.split("\n")):
			line = raw_line.strip()

			if line.startswith("-- name:"):
				if current_name and current_lines:
					self.add_prepared_statement(
						current_name,
						current_lines,
						idx - len(current_lines)
					)

					current_name = ""
					current_lines = []

				current_name = line[8:].strip()

				if not current_name:
					raise StatementParsingError(
						"Statement name cannot be empty",
						current_name,
						idx,
						8
					)

			elif line.startswith("--") or not current_name:
				continue

			elif ";" in raw_line and statement_end:
				raise StatementParsingError(
					"Statements can only have one query",
					current_name,
					idx,
					raw_line.index(";")
				)

			else:
				current_lines.append(line)

		if current_name and current_lines:
			self.add_prepared_statement(current_name, current_lines, idx - len(current_lines))


class Cursor:
	"Represents a connection cursor. Can be used like a context manager and iterable."

	def __init__(self, conn: Connection, cursor: CursorProto):
		"""
			Create a new cursor object

			:param conn: Connection to create the cursor for
			:param cursor: Backend cursor object to wrap
		"""

		self.connection: Connection = conn
		"Connection object the cursor is associated with"

		self._cur: CursorProto | None = cursor
		self._trans = False


	def __enter__(self) -> Cursor:
		return self


	def __exit__(self, *_) -> None:
		self.close()


	def __iter__(self) -> Cursor:
		return self


	def __next__(self) -> Row:
		if not (row := self.one()):
			self.close()
			raise StopIteration

		return row


	@property
	def description(self) -> Iterator[ColumnDescription]:
		"Get a description of the columns of the returned data"

		if self._cur is None:
			raise ConnectionError("Cursor closed")

		for column in self._cur.description:
			yield ColumnDescription(*column)


	@property
	def row_count(self) -> int:
		"Return the number of rows affected by the last executed query"

		if self._cur is None:
			raise ConnectionError("Cursor closed")

		return self._cur.rowcount


	def close(self) -> None:
		"Close the cursor"

		if self._cur is None:
			return

		self._cur.close
		self._cur = None


	def execute(self, query: str, params: dict[str, Any] | None = None) -> None:
		"""
			Execute an SQL query. Placeholders use the ``:{name}`` convention.

			:param query: SQL statement to be executed
			:param params: Parameters to be used when replacing the placeholders in the query.
		"""

		if self._cur is None:
			raise ConnectionError("Cursor closed")

		self._cur.execute(query, params or {})

		if query.lower().startswith(TRANS_QUERIES):
			self.connection._trans = True

		elif query.lower().startswith(("commit", "rollback")):
			self.connection._trans = False


	def execute_many(self, query: str, params: Iterable[dict[str, Any]]) -> None:
		"""
			Execute an SQL query multiple sets of parameters. Placeholders use the ``:{name}``
				convention.

			:param query: SQL statement to be executed
			:param params: List of parameters to be used when replacing the placeholders in the
				query.
		"""

		if self._cur is None:
			raise ConnectionError("Cursor closed")

		self._cur.executemany(query, params)


	def query(self, statement: Statement) -> None:
		"""
			Execute a ``Statement`` object

			:param statement: ``Statement`` object to be executed
		"""

		query, params = statement.build(self.connection.database.backend_type)
		self.execute(query, params)


	def run(self, name: str, params: dict[str, Any] | None = None) -> None:
		"""
			Execute a prepared statement

			:param name: Name of the prepared statement
			:param params: Parameters to be used when replacing the placeholders in the query
		"""

		self.execute(self.connection.database.prepared_statements[name], params)


	def one(self) -> Row | None:
		"Return a single row."

		if self._cur is None:
			raise ConnectionError("Cursor closed")

		if not (row := self._cur.fetchone()):
			self.close()
			return None

		return Row.from_cursor(self, row)


	def many(self, count: int = 1) -> Iterator[Row]:
		"""
			Return up to the specified number of rows.

			:param count: Max number of rows to return.
		"""

		if self._cur is None:
			raise ConnectionError("Cursor closed")

		for row in self._cur.fetchmany(count):
			yield Row.from_cursor(self, row)

		self.close()


	def all(self) -> Iterator[Row]:
		"Return all rows."

		for row in self:
			yield row
