import prompt
import shlex
from src.primitive_db.utils import load_metadata, save_metadata
from src.primitive_db.core import create_table, drop_table, list_tables
from pathlib import Path

DB_FILE = Path(__file__).resolve().parents[2] / "db_meta.json"

# DB_FILE = "db_meta.json"

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

def print_help():
	"""Выводит справочную информацию."""
	print("\n***Процесс работы с таблицей***")
	print("Функции:")
	print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
	print("<command> list_tables - показать список всех таблиц")
	print("<command> drop_table <имя_таблицы> - удалить таблицу")
	print("<command> exit - выход из программы")
	print("<command> help - справочная информация\n")

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

			case "list_tables":
				list_tables(metadata)

			case "help":
				print_help()

			case "exit":
				print("Выход из программы...")
				break

			case _:
				print(f"Функции {command} нет. Попробуйте снова или вызовите справочник"
				      f"по команде 'help'.")