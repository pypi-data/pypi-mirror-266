from __future__ import annotations

import typing

from dataclasses import dataclass

from .enums import Comparison, OrderDirection

if typing.TYPE_CHECKING:
	from typing import Any
	from .enums import BackendType

	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


@dataclass()
class Where:
	"Represents a single comparison in a ``WHERE`` block"

	key: str
	"Column to compare the data to"

	value: str
	"Data to compare with"

	comparison: Comparison
	"What kind of comparison to do between the column and data"

	operation: str
	"Operation to use with the previous comparison"


	def build(self, include_operation: bool = False) -> str:
		"""
			Convert the object into a string

			:param include_operation: Append :attr:`Where.operation` to the start of the string
		"""

		data = f"\"{self.key}\" {self.comparison.value} :where_{self.key}"

		if include_operation:
			return f"{self.operation} {data}"

		return data


@dataclass()
class OrderBy:
	"Represents a single column/direction pair in an `ORDER BY` block"

	column: str
	"The column to sort"

	direction: OrderDirection = OrderDirection.ASCENDING
	"The direction to sort the data"


	def __post_init__(self):
		self.direction = OrderDirection.parse(self.direction)


class Statement:
	"Represents an SQL query"

	def __init__(self, table: str):
		"""
			Create a new ``Statement`` object

			.. note::
				Do not initiate this statement by itself. Sub-class this class to implement a
				statement type.

			:param table: Name of the table to work with
		"""

		if type(self) is Statement:
			raise NotImplementedError("Statement class cannot be initiated")

		self.table: str = table
		self.where: list[Where] = []
		self.params: dict[str, Any] = {}
		self.limit: int = 0
		self.offset: int = 0
		self.order_by: list[OrderBy] = []
		self.return_rows: bool = False


	def _build_data(self) -> list[str]:
		data = []

		if self.where:
			data.append("WHERE")

			for idx, item in enumerate(self.where):
				data.append(item.build(True if idx > 0 else False))

		if self.order_by:
			items = tuple(f"\"{item.column}\" {item.direction.value}" for item in self.order_by)

			data.append("ORDER BY")
			data.append(", ".join(items))

		if self.offset:
			data.append(f"OFFSET {self.offset}")

		if self.limit:
			data.append(f"LIMIT {self.limit}")

		if self.return_rows:
			data.append("RETURNING *")

		return data


	def set_limit(self, limit: int) -> Self:
		"""
			Set the maximum number of rows to return from the query

			:param limit: Max number of rows to return
		"""

		self.limit = limit
		return self


	def set_offset(self, offset: int) -> Self:
		"""
			Row index to start returning rows from

			:param offset: Row index to start with
		"""

		self.offset = offset
		return self


	def set_order_by(self, column: str, direction: OrderDirection | str) -> Self:
		"""
			Order the returned rows by the specified column and order

			:param column: Table column to sort by
			:param direction: Direction to sort the column
		"""

		self.order_by.append(OrderBy(column, OrderDirection.parse(direction)))
		return self


	def set_where(self,
				key: str,
				value: str,
				comparison: Comparison | str = Comparison.EQUAL,
				operation: str = "AND") -> Self:
		"""
			Append a comparison to the ``WHERE`` block of the statement

			:param key: Column to compare the data to
			:param value: Data to compare with
			:param comparison: What kind of comparison to do between the column and data
			:param operation: Operation to use with the previous comparison
		"""


		self.where.append(Where(key, value, Comparison.parse(comparison), operation))
		self.params[f"where_{key}"] = value
		return self


	def build(self, btype: BackendType) -> tuple[str, dict[str, Any]]:
		"""
			Convert the ``Statement`` object to an SQL query

			:param btype: The database backend type to build the string for
		"""

		raise NotImplementedError("no")


class Select(Statement):
	"Represents a ``SELECT`` SQL query"

	def __init__(self,
				table: str,
				columns: list[str] | None = None,
				limit: int = 0,
				offset: int = 0):
		"""
			Create a new ``Select`` statement

			:param table: Name of the table to work with
			:param columns: Columns to return from each row. Use ``None`` to return all columns.
			:param limit: Maximum number of rows to return
			:param offset: Row number to start with
		"""

		Statement.__init__(self, table)

		self.columns: list[str] = columns or []
		self.limit: int = limit
		self.offset: int = offset


	def build(self, btype: BackendType) -> tuple[str, dict[str, Any]]:
		data = [
			"SELECT",
			",".join(self.columns) if self.columns else "*",
			"FROM",
			f"\"{self.table}\"",
			*self._build_data()
		]

		return " ".join(data), self.params


class Insert(Statement):
	"Represents an ``INSERT`` SQL query"

	def __init__(self,
				table: str,
				data: dict[str, Any],
				return_rows: bool = True):
		"""
			Create a new ``Insert`` statement

			:param table: Name of the table to work with
			:param data: Row data to be inserted
			:param return_rows: Return the newly inserted row
		"""

		Statement.__init__(self, table)

		self.return_rows: bool = return_rows
		self.keys: list[str] = []

		self.set_data(data)


	def set_data(self, data: dict[str, Any]) -> Self:
		"""
			Set the key/value pairs to be inserted

			:param data: Dict of key/value pairs
		"""

		self.keys.extend(data.keys())
		self.params.update(data)
		return self


	def build(self, btype: BackendType) -> tuple[str, dict[str, Any]]:
		keys = ", ".join(self.keys)
		values = ", ".join(f":{key}" for key in self.keys)
		data = [
			f"INSERT INTO \"{self.table}\" ({keys}) VALUES ({values})",
			*self._build_data()
		]

		return " ".join(data), self.params


class Update(Insert):
	"Represents an ``UPDATE`` SQL query"

	def __init__(self,
				table: str,
				data: dict[str, Any],
				limit: int = 0,
				offset: int = 0,
				return_rows: bool = True):
		"""
			Create a new ``Update`` statement

			:param table: Name of the table to work with
			:param data: Row data to insert
			:param limit: Maximum number of rows to update
			:param offset: Row number to start with
			:param return_rows: Return the newly inserted row
		"""

		Insert.__init__(self, table, data, return_rows)

		self.limit: int = limit
		self.offset: int = offset


	def build(self, btype: BackendType) -> tuple[str, dict[str, Any]]:
		pairs = ", ".join(f"\"{key}\" = :{key}" for key in self.keys)
		data = [
			f"UPDATE \"{self.table}\" SET",
			pairs,
			*self._build_data()
		]

		return " ".join(data), self.params


class Delete(Statement):
	"Represents a ``Delete`` SQL query"

	def __init__(self, table: str, limit: int = 0, offset: int = 0):
		"""
			Create a new ``Delete`` statement

			:param table: Name of the table to work with
			:param limit: Maximum number of rows delete
			:param offset: Row number to start with
		"""

		Statement.__init__(self, table)

		self.limit: int = limit
		self.offset: int = offset


	def build(self, btype: BackendType) -> tuple[str, dict[str, Any]]:
		data = [
			f"DELETE FROM \"{self.table}\"",
			*self._build_data()
		]

		return " ".join(data), self.params
