from __future__ import annotations

import json
import typing

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path

from .enums import BackendType
from .misc import ClassProperty, boolean

if typing.TYPE_CHECKING:
	from collections.abc import Iterable
	from typing import Any
	from types import ModuleType
	from .database import Connection, Database
	from .misc import ConnectionProto


BACKENDS: dict[str, type[Backend]] = {}


class Backend(ABC):
	"""
		Represents a DBAPI module. Sub-class this class and register it with :meth:`Backend.set`
		to add another backend
	"""

	module_name: str
	"""
		DBAPI 2.0 module to import. The module should have a ``connect`` method and ``paramstyle``
		property.
	"""

	backend_type: BackendType
	"Database type for the backend"


	@ClassProperty
	def name(cls) -> str:
		"Get the name of the backend in lowercase."

		return cls.__name__.lower() # type: ignore


	@staticmethod
	def get(name: str) -> type[Backend]:
		"""
			Get the backend with the specified name.

			:param name: Name of the backend to get
		"""

		return BACKENDS[name.lower()]


	@staticmethod
	def set(backend: type[Backend]) -> type[Backend]:
		"""
			Register a backend to be used with :class:`Database`. Can be used as a decorator.

			:param backend: Backend-based class to register
		"""

		if backend.name in BACKENDS:
			raise ValueError(f"Backend already registered: {backend.name}")

		BACKENDS[backend.name] = backend
		return backend


	@property
	def module(self) -> ModuleType:
		"Import the module, set ``paramstyle`` to ``named``, and return it."
		module = import_module(self.module_name)
		module.paramstyle = "named" # type: ignore
		return module


	@abstractmethod
	def get_connection(self, database: Database) -> ConnectionProto:
		"""
			Call the module's ``connect`` method and return the resulting connection.

			:param database: Database object to get the config from
		"""
		...


	@abstractmethod
	def get_databases(self, conn: Connection) -> Iterable[str]:
		"""
			Get a list of databases in the server

			:param conn: Database connection to use
		"""
		...


	@abstractmethod
	def get_tables(self, conn: Connection) -> Iterable[str]:
		"""
			Get a list of the tables in a database

			:param conn: Database connection to use
		"""
		...


@Backend.set
class Sqlite3(Backend):
	"Supports connecting to sqlite databases with the :mod:`sqlite3` module."

	module_name = "sqlite3"
	backend_type = BackendType.SQLITE


	def __init__(self) -> None:
		self.module.register_adapter(datetime, lambda v: v.timestamp())
		self.module.register_adapter(dict, json.dumps)
		self.module.register_adapter(list, json.dumps)
		self.module.register_adapter(tuple, json.dumps)
		self.module.register_adapter(set, json.dumps)
		self.module.register_adapter(bool, lambda v: boolean(v.decode("utf-8")))

		self.module.register_converter("timestamp", Sqlite3.deserialize_timestamp)
		self.module.register_converter("datetime", Sqlite3.deserialize_timestamp)
		self.module.register_converter("json", json.loads)
		self.module.register_converter("boolean", lambda v: True if v == b"1" else False)
		self.module.register_converter("real", float)
		self.module.register_converter("integer", int)

	@staticmethod
	def deserialize_timestamp(raw_value: bytes) -> datetime:
		"""
			Method used to serialize ``TIMESTMAP`` and ``DATETIME`` column values.
		"""

		value = raw_value.decode("utf-8")

		try:
			return datetime.fromtimestamp(float(value), tz = timezone.utc)

		except ValueError:
			return datetime.fromisoformat(value)


	def get_connection(self, database: Database) -> Any:
		options = database.arguments.copy()

		if "check_same_thread" not in options:
			options["check_same_thread"] = False

		return self.module.connect(
			database.database,
			detect_types = self.module.PARSE_DECLTYPES,
			# autocommit = False,
			**options
		)


	def get_databases(self, conn: Connection) -> Iterable[str]:
		return tuple([])


	def get_tables(self, conn: Connection) -> Iterable[str]:
		with conn.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'") as cur:
			return tuple(row["tbl_name"] for row in cur)


@Backend.set
class PG8000(Backend):
	"Supports connecting to postgresql databases with the :mod:`pg8000` module."

	module_name = "pg8000.dbapi"
	backend_type = BackendType.POSTGRESQL


	def connect(self, database: Database) -> ConnectionProto:
		options = {
			"user": database.username,
			"password": database.password or "",
			"database": database.database,
			"host": database.host,
			"port": database.port
		}

		if isinstance(database.host, Path):
			path = options.pop("host")
			port = options.pop("port")
			options["unix_sock"] = f"{path}/.s.PGSQL.{port}"

		return self.module.connect(**options, **database.arguments)


	def get_databases(self, conn: Connection) -> Iterable[str]:
		query = "SELECT datname FROM pg_database WHERE datistemplate = false"

		with conn.execute(query) as cur:
			return tuple(row["datname"] for row in cur)


	def get_tables(self, conn: Connection) -> Iterable[str]:
		query = "SELECT tablename FROM pg_catalog.pg_tables WHERE "
		query += "schemaname != 'pg_catalog' AND schemaname != 'information_schema'"

		with conn.execute(query) as cur:
			return tuple(row["tablename"] for row in cur)
