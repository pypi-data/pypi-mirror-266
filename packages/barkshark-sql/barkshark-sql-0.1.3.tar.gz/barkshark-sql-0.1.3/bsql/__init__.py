__software__ = "Barkshark SQL"
__version__ = "0.1.3"
__author__ = "Zoey Mae"
__homepage__ = "https://git.barkshark.xyz/barkshark/bsql"

from .backends import Backend, PG8000, Sqlite3
from .database import Connection, Cursor, Database
from .enums import BackendType, Comparison, OrderDirection, StrEnum
from .table import Tables, Table, Column
from .statement import Statement, Select, Insert, Update, Delete, Where, OrderBy

from .misc import (
	ColumnDescription,
	ConnectionProto,
	CursorProto,
	Row,
	StatementParsingError,
	boolean
)
