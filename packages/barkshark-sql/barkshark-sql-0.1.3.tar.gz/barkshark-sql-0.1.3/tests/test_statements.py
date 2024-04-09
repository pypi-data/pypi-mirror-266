from bsql import Select, Insert, Update, Delete
from bsql import BackendType, Comparison, OrderDirection

from .data import USERS


RESULTS = {
	
}


def test_select():
	stmt = Select("users")
	stmt.set_where("gay_level", 9000, Comparison.GREATER)
	stmt.set_where("gender", "demigirl", Comparison.EQUAL, "OR")
	query, params = stmt.build(BackendType.SQLITE)

	assert query == "SELECT * FROM \"users\" WHERE \"gay_level\" > :where_gay_level OR \"gender\" = :where_gender"
	assert params == {"where_gay_level": 9000, "where_gender": "demigirl"}


def test_select_limit_offset():
	stmt = Select("users").set_limit(100).set_offset(200)
	query, params = stmt.build(BackendType.SQLITE)

	assert query == "SELECT * FROM \"users\" OFFSET 200 LIMIT 100"
	assert params == {}


def test_select_orderby():
	stmt = Select("users").set_order_by("name", "DESC").set_order_by("gayness", OrderDirection.ASCENDING)
	query, params = stmt.build(BackendType.POSTGRESQL)

	assert query == "SELECT * FROM \"users\" ORDER BY \"name\" DESC, \"gayness\" ASC"
	assert params == {}


def test_insert():
	for user in USERS:
		stmt = Insert("users", user)
		query, params = stmt.build(BackendType.SQLITE)

		assert query == "INSERT INTO \"users\" (name, species, gender, gay_level) VALUES (:name, :species, :gender, :gay_level) RETURNING *"
		assert params == user


def test_update():
	stmt = Update("users", {"gay_level": 9002}).set_where("name", "izalia")
	query, params = stmt.build(BackendType.SQLITE)

	assert query == "UPDATE \"users\" SET \"gay_level\" = :gay_level WHERE \"name\" = :where_name RETURNING *"
	assert params == {"gay_level": 9002, "where_name": "izalia"}


def test_delete():
	stmt = Delete("users").set_where("name", "zoey")
	query, params = stmt.build(BackendType.SQLITE)

	assert query == "DELETE FROM \"users\" WHERE \"name\" = :where_name"
	assert params == {"where_name": "zoey"}
