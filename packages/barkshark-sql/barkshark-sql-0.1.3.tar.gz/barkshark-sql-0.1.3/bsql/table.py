from __future__ import annotations

import json
import typing

from pathlib import Path

from .enums import BackendType

if typing.TYPE_CHECKING:
	from typing import Any


class Tables(dict):
	"Holds the table layouts for a database"

	def __init__(self, *tables: Table):
		"""
			Create a new ``Tables`` object

			:param tables: ``Table`` objects to initiate with
		"""

		dict.__init__(self, {table.name: table for table in tables})


	@classmethod
	def from_json(cls: type[Tables], raw_data: Path | str | dict[str, Any]) -> Tables:
		"""
			Create a new ``Tables`` object from a JSON file, JSON string, or ``dict`` object

			:param raw_data: Data to parse into tables
		"""

		tables = cls()
		tables.load_json(raw_data)

		return tables


	def add_table(self, table: Table) -> None:
		"""
			Append a table to the list of tables

			:param table: The table to add
		"""

		self[table.name] = table


	def new_table(self, name: str, *columns: Column) -> Table:
		"""
			Create a new table and append it to the list of tables

			:param name: Name of the table to create
			:param columns: List of ``Column`` objects for the table
		"""

		self[name] = Table(name, *columns)
		return self[name]


	def build(self, btype: BackendType) -> tuple[str]:
		"""
			Convert each table object into an SQL query string

			:param btype: Backend database type to build the query for
		"""

		return tuple(table.build(btype) for table in self.values())


	def load_json(self, raw_data: Path | str | dict[str, Any]) -> None:
		"""
			Load new ``Table`` objects from a JSON file, JSON string, or ``dict`` object

			:param raw_data: Data to parse into tables
		"""

		if isinstance(raw_data, str):
			if (path := Path(raw_data).expanduser().resolve()).exists():
				raw_data = path

			else:
				data = json.loads(raw_data)

		if isinstance(raw_data, Path):
			with raw_data.open("r", encoding = "utf-8") as fd:
				data = json.load(fd)

		elif not isinstance(raw_data, dict):
			raise TypeError("Data is not a Path, str, or dict")

		else:
			data = raw_data

		for table_name, table in data.items():
			self.new_table(table_name)

			for column_name, column in table.items():
				self[table_name].new_column(column_name, column.pop("type"), **column)


	def to_dict(self) -> dict[str, Any]:
		"""
			Convert all tables to a ``dict`` object that can later be loaded with
			:meth:`Tables.load_json` or :meth:`Tables.from_json`
		"""

		data: dict[str, Any] = {}

		for table in self.values():
			data[table.name] = {}

			for column in table.values():
				data[table.name][column.name] = {
					"type": column.data_type,
					"nullable": column.nullable,
					"autoincrement": column.autoincrement,
					"primary_key": column.primary_key,
					"default": column.default,
					"unique": column.unique,
					"foreign_key": column.foreign_key
				}

		return data


	def to_json(self, path: Path | str | None = None, indent: int | str | None = "\t") -> str:
		"""
			Dump the tables to a JSON string and optionally to a file

			:param path: Path to store the tables as a JSON file
			:param indent: Number of spaces (int) or string (str) to use for indentions in the
				resulting JSON data
		"""

		if isinstance(path, str):
			path = Path(path).expanduser().resolve()

		if path:
			with path.open("w", encoding = "utf-8") as fd:
				json.dump(self.to_dict(), fd, indent = indent)

		return json.dumps(self.to_dict(), indent = indent)


class Table(dict):
	"Represents a table"

	def __init__(self, name: str, *columns: Column, schema_name: str = ""):
		"""
			Create a new ``Table`` object

			:param name: Name of the table
			:param columns: Columns of the table
			:param schema_name: Schema name to use
		"""

		dict.__init__(self, {column.name: column for column in columns})

		self.name: str = name
		self.schema_name: str = schema_name


	def add_column(self, column: Column) -> Column:
		"""
			Append an existing ``Column`` object to the table

			:param column: Column to append
		"""

		self[column.name] = column
		return column


	def new_column(self, name, *args, **kwargs) -> Column:
		"""
			Append a new ``Column`` object to the table

			:param name: Name of the column
			:param args: Positional arguments to pass to :meth:`Column.__init__`
			:param kwargs: Keyword arguments to pass to :meth:`Column.__init__`
		"""

		self[name] = Column(name, *args, **kwargs)
		return self[name]


	def build(self, btype: BackendType) -> str:
		"""
			Convert the table object into an SQL query string

			:param btype: Backend database type to build the query for
		"""

		foreign_keys: list[str] = []
		columns: list[str] = []

		for column in self.values():
			columns.append(column.build(btype))

			if column.foreign_key:
				table, col = column.foreign_key

				fkey_string = f"\tFOREIGN KEY (\"{column.name}\")\n"
				fkey_string += f"\t\tREFERENCES \"{table}\" (\"{col}\")\n"
				fkey_string += "\t\t\tON DELETE CASCADE"

				foreign_keys.append(fkey_string)

		column_string = "\t" + ",\n\t".join(columns)

		if foreign_keys:
			column_string += ",\n" + ", ".join(foreign_keys)

		if self.schema_name:
			table_name = f"\"{self.schema_name}\".\"{self.name}\""

		else:
			table_name = f"\"{self.name}\""

		return f"CREATE TABLE IF NOT EXISTS {table_name} (\n{column_string}\n);"


class Column:
	"Represents a column in a table"

	def __init__(self,
				name: str,
				data_type: str,
				nullable: bool = True,
				autoincrement: bool = False,
				primary_key: bool = False,
				default: str = "",
				unique: bool = False,
				foreign_key: tuple[str, str] | None = None):
		"""
			Create a new ``Column`` object

			:param name: Name of the column
			:param data_type: Type of data to be stored in the column
			:param nullable: Whether or not the data for the column can be ``NULL``
			:param autoincrement: Ensure an ``INTEGER PRIMARY KEY`` column does not reuse numbers
				(sqlite-only)
			:param primary_key: Set the column to be a primary column
			:param default: Value to set for a row if the value is ``NULL``
			:param unique: Ensure every row for this column has a unique value
			:param foreign_key: Column from another table this column should reference
		"""

		self.name: str = name
		"Name of the column"

		self.data_type: str = data_type.upper()
		"Type of data to be stored in the column"

		self.nullable: bool = nullable
		"Whether or not the data for the column can be ``NULL``"

		self.autoincrement: bool = autoincrement
		"Ensure an ``INTEGER PRIMARY KEY`` column does not reuse numbers (sqlite-only)"

		self.primary_key: bool = primary_key
		"Set the column to be a primary column"

		self.default: str = default
		"Value to set for a row if the value is ``NULL``"

		self.unique: bool = unique
		"Ensure every row for this column has a unique value"

		self.foreign_key: tuple[str, str] | None = foreign_key
		"Column from another table this column should reference"


	def build(self, btype: BackendType) -> str:
		"""
			Convert the column object into an SQL query string to be used in a ``CREATE TABLE``
			query

			:param btype: Backend database type to build the query for
		"""

		data = [f"\"{self.name}\""]

		if self.data_type == "SERIAL":
			if btype == BackendType.POSTGRESQL:
				data.extend([self.data_type, "PRIMARY KEY"])

			else:
				data.extend(["INTEGER", "UNIQUE", "PRIMARY KEY"])

			return " ".join(data)

		data.append(self.data_type)

		if not self.nullable:
			data.append("NOT NULL")

		if self.unique:
			data.append("UNIQUE")

		if self.primary_key:
			data.append("PRIMARY KEY")

		if self.autoincrement and btype == BackendType.SQLITE:
			data.append("AUTOINCREMENT")

		if self.default:
			data.append(f"DEFAULT {repr(self.default)}")

		return " ".join(data)
