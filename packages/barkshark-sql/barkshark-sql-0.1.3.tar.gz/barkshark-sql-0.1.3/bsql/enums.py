from __future__ import annotations

import typing

from enum import Enum

if typing.TYPE_CHECKING:
	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


class StrEnum(str, Enum):
	"Base class for :class:`str`-based enums"

	def __new__(cls: type[Self], value: str) -> Self:
		return str.__new__(cls, value)


	@classmethod
	def parse(cls: type[Self], value: str) -> Self:
		"""
			Return an enum value based on a string

			:param value: String to use to find an enum value
		"""

		if isinstance(value, cls):
			return value

		try:
			return cls[value]

		except KeyError:
			pass

		return cls(value)


class BackendType(StrEnum):
	"Type of database the backend connects to"

	POSTGRESQL = "postgresql"
	SQLITE = "sqlite"


class Comparison(StrEnum):
	"Comparison types usually used for the WHERE section in SQL queries"

	LESS = "<"
	GREATER = ">"
	LESS_EQUAL = "<="
	GREATER_EQUAL = ">="
	EQUAL = "="
	NOT_EQUAL = "!="
	IN = "IN"
	NOT_INT = "NOT IN"
	LIKE = "LIKE"
	NOT_LIKE = "NOT LIKE"
	IS_NULL = "IS NULL"
	NOT_NULL = "IS NOT NULL"


class OrderDirection(StrEnum):
	"Direction to sort row"

	ASCENDING = "ASC"
	DESCENDING = "DESC"
