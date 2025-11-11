import shlex
from pathlib import Path
from typing import Any

import prompt

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

DB_FILE = Path(__file__).resolve().parents[2] / "db_meta.json"

# DB_FILE = "db_meta.json"
# TODO: перепроверить парсеры тоже
def parse_where(tokens: list[str]) -> dict[str, Any] | None:
	"""
	Парсит выражение WHERE в словарь.

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

def welcome():
	"""
	Функция-хелпер: выводит доступные команды, считывает команды с консоли и реагирует
	"""
	print("***")
	print("<command> exit - выйти из программы")
	print("<command> help - справочная информация\n")

	command = prompt.string('Введите команду: ')
	match command:
		case "exit":
			print("Выход из программы...")

		case "help":
			print("\n<command> exit - выйти из программы")
			print("<command> help - справочная информация\n")
			welcome()

		case _:
			print(f"Неизвестная команда: {command}\n")
			welcome()

def print_help() -> None:
	"""Выводит справочную информацию по командам."""
	print("\n***Операции с данными***")
	print("Функции:")
	print("<command> insert into <имя_таблицы> values (...) - добавить запись")
	print("<command> select from <имя_таблицы> [where <столбец> = <значение>] - "
                                                                    "показать записи")
	print("<command> update <имя_таблицы> set <столбец> = <значение> where ... -"
                                                                    " обновить запись")
	print("<command> delete from <имя_таблицы> where <столбец> = <значение> - "
                                                                    "удалить запись")
	print("<command> info <имя_таблицы> - информация о таблице")
	print("<command> exit - выход из программы")
	print("<command> help - справка\n")

def run():
	"""Главный цикл программы."""
	print("***База данных***")
	print_help()

	while True:
		user_input = input(">>> Введите команду: ").strip()

		if not user_input:
			continue

		try:
			args = shlex.split(user_input)
		except ValueError:
			print("Некорректный ввод. Попробуйте снова.")
			continue

		command = args[0]
		metadata = load_metadata(DB_FILE)

		match command:
			case "create_table":
				if len(args) < 2:
					print("Ошибка: Слишком мало аргументов.")
					continue
				table_name = args[1]
				columns = args[2:]
				updated = create_table(metadata, table_name, columns)
				save_metadata(DB_FILE, updated)

			case "drop_table":
				if len(args) != 2:
					print("Ошибка: укажите имя таблицы.")
					continue
				table_name = args[1]
				updated = drop_table(metadata, table_name)
				save_metadata(DB_FILE, updated)

			case "insert":
				if len(args) < 5 or args[1] != "into" or args[3] != "values":
					print("Ошибка синтаксиса. Пример: insert into <table> values (...)")
					continue
				table_name = args[2]
				values_str = " ".join(args[4:])
				# values = shlex.split(values_str.strip("()"), )
				values = values_str.strip("()").split(", ")
				insert(metadata, table_name, values)

			case "select":
				if len(args) < 3 or args[1] != "from":
					print("Ошибка синтаксиса. Пример: select from <table>")
					continue
				table_name: str = args[2]
				table_data: list[dict] = load_table_data(table_name)

				where_clause: dict | None = None
				if len(args) > 3 and args[3] == "where":
					where_clause = parse_where(args[4:])

				select(table_data, where_clause)

			case "update":
				if "set" not in args or "where" not in args:
					print("Ошибка синтаксиса. Пример: update <table> set x=1 where y=2")
					continue
				table_name: str = args[1]
				table_data: list[dict] = load_table_data(table_name)

				set_index: int = args.index("set")
				where_index: int = args.index("where")

				set_clause: dict | None = parse_set(args[set_index + 1:where_index])
				where_clause: dict | None = parse_where(args[where_index + 1:])

				if set_clause and where_clause:
					updated_data: list[dict] = update(table_data, set_clause,
																		where_clause)
					save_table_data(table_name, updated_data)

			case "delete":
				if len(args) < 6 or args[1] != "from" or args[3] != "where":
					print("Ошибка синтаксиса. Пример: delete from <table> where x=1")
					continue
				table_name: str = args[2]
				table_data: list[dict] = load_table_data(table_name)

				where_clause: dict | None = parse_where(args[4:])
				if where_clause:
					new_data: list[dict] = delete(table_data, where_clause)
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
