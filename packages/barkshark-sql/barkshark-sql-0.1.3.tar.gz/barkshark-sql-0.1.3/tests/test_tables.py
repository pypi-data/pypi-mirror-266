import bsql as bsql

from .data import FILES, TABLES


def test_json_import():
	tables = bsql.Tables.from_json(FILES["input-tables"])
	assert tables.to_json() == TABLES.to_json()


def test_json_export():
	with FILES["output-tables"].open("r", encoding = "utf-8") as fd:
		assert fd.read() == TABLES.to_json()


def test_postgresql_build():
	with FILES["tables-postgresql"].open("r", encoding = "utf-8") as fd:
		assert fd.read() == "\n\n".join(TABLES.build(bsql.BackendType.POSTGRESQL))


def test_sqlite_build():
	with FILES["tables-sqlite"].open("r", encoding = "utf-8") as fd:
		assert fd.read() == "\n\n".join(TABLES.build(bsql.BackendType.SQLITE))
