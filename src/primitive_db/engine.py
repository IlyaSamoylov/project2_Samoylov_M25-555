import shlex
from typing import Any

import prompt

from src.primitive_db.constants import DB_META_FILE
from src.primitive_db.core import (
	create_table,
	delete,
	drop_table,
	info,
	insert,
	list_tables,
	select,
	update,
)
from src.primitive_db.utils import (
	load_metadata,
	load_table_data,
	save_metadata,
	save_table_data,
)


def parse_where(tokens: list[str]) -> dict[str, Any] | None:
	"""
	Парсит выражение WHERE в словарь.

	:param tokens: (list[str]) разбитое считанное условие where

	:return: (dict[str, Any] | None) словарь ключ-значение для where, либо None, если
	where не было

	Пример:
	>>> parse_where(["age", "=", "28"])
	{'age': '28'}
	"""

	try:
		if len(tokens) < 3 or tokens[1] != "=":
			raise ValueError
		key = tokens[0]
		val = tokens[2].strip('"').strip("'")
		return {key: val}
	except Exception:
		print("Ошибка: некорректное условие WHERE.")
		return None


def parse_set(tokens: list[str]) -> dict[str, Any] | None:
	"""
	Парсит выражение SET в словарь.

	:param tokens: (list[str]) разбитое считанное условие set

	:return: (dict[str, Any] | None) словарь ключ-значение для set, либо None, если
	set не было

	Пример:
	>>> parse_set(["age", "=", "30"])
	{'age': '30'}
	"""
	try:
		if len(tokens) < 3 or tokens[1] != "=":
			raise ValueError
		key = tokens[0]
		val = tokens[2].strip('"').strip("'")
		return {key: val}
	except Exception:
		print("Ошибка: некорректный SET.")
		return None

def print_help() -> None:
	"""Выводит справочную информацию по командам."""
	print("\n***Операции с таблицами***")
	print("create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ... - создать "
																			"таблицу")
	print("drop_table <имя_таблицы> - удалить таблицу (с подтверждением)")
	print("list_tables - показать список всех таблиц")

	print("\n***Операции с данными***")
	print("insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - "
																	"добавить запись")
	print("select from <имя_таблицы> [where <столбец> = <значение>] - показать записи")
	print("update <имя_таблицы> set <столбец> = <значение> where <столбец> = <значение>"
																" - обновить запись")
	print("delete from <имя_таблицы> where <столбец> = <значение> - удалить запись"
																" (с подтверждением)")
	print("info <имя_таблицы> - информация о структуре таблицы")

	print("\n***Дополнительно***")
	print("help - показать эту справку")
	print("exit - выйти из программы")

def run():
	"""Главный цикл программы."""
	print("***База данных***")
	print_help()

	while True:
		user_input = prompt.string(">>> Введите команду: ").strip()

		if not user_input:
			continue

		try:
			args = shlex.split(user_input)
		except ValueError:
			print("Некорректный ввод. Попробуйте снова.")
			continue

		command = args[0]
		metadata = load_metadata(DB_META_FILE)

		match command:
			case "create_table":
				if len(args) < 2:
					print("Ошибка: Слишком мало аргументов.")
					continue
				table_name = args[1]
				columns = args[2:]
				updated = create_table(metadata, table_name, columns)
				save_metadata(DB_META_FILE, updated)

			case "drop_table":
				if len(args) != 2:
					print("Ошибка: укажите имя таблицы.")
					continue
				table_name = args[1]
				updated = drop_table(metadata, table_name)
				save_metadata(DB_META_FILE, updated)

			case "insert":
				if len(args) < 5 or args[1] != "into" or args[3] != "values":
					print("Ошибка синтаксиса. Пример: insert into <table> values (...)")
					continue
				table_name = args[2]
				values_str = " ".join(args[4:])
				values = values_str.strip("()").split(", ")
				insert(metadata, table_name, values)

			case "select":
				if len(args) < 3 or args[1] != "from":
					print("Ошибка синтаксиса. Пример: select from <table>")
					continue
				table_name = args[2]
				table_data = load_table_data(table_name)

				where_clause = None
				if len(args) > 3 and args[3] == "where":
					where_clause = parse_where(args[4:])

				select(table_data, where_clause)

			case "update":
				if "set" not in args or "where" not in args:
					print("Ошибка синтаксиса. Пример: update <table> set x=1 where y=2")
					continue
				table_name = args[1]
				table_data = load_table_data(table_name)

				set_index = args.index("set")
				where_index = args.index("where")

				set_clause = parse_set(args[set_index + 1:where_index])
				where_clause = parse_where(args[where_index + 1:])

				if set_clause and where_clause:
					updated_data = update(table_data, set_clause, where_clause)
					save_table_data(table_name, updated_data)

			case "delete":
				if len(args) < 6 or args[1] != "from" or args[3] != "where":
					print("Ошибка синтаксиса. Пример: delete from <table> where x=1")
					continue
				table_name = args[2]
				table_data = load_table_data(table_name)

				where_clause = parse_where(args[4:])
				if where_clause:
					new_data = delete(table_data, where_clause)
					save_table_data(table_name, new_data)


			case "list_tables":
				list_tables(metadata)

			case "help":
				print_help()

			case "info":
				if len(args) != 2:
					print("Ошибка: укажите имя таблицы.")
					continue
				info(metadata, args[1])

			case "exit":
				print("Выход из программы...")
				break

			case _:
				print(f"Функции {command} нет. Попробуйте снова или вызовите справочник"
																f"по команде 'help'.")
