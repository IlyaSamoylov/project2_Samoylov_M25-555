from typing import Any
from prettytable import PrettyTable
from src.primitive_db.utils import load_table_data, save_table_data

VALID_TYPES = {"int", "str", "bool"}

def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
	"""
	Создает таблицу, если другой с таким именем не существует,  добавляя её описание в
	метаданные. Автоматически добавляет столбце ID: int в начало.
	:param:
		metadata: (dict) словарь метаданных для таблицы
		table_name: (str) имя новой таблицы
		columns: (list[str]) список столбцов
	:returns:
		(dict) словарь метаданных таблицы
	"""
	if table_name in metadata:
		print(f'Ошибка: Таблица "{table_name}" уже существует.')
		return metadata

	# Добавляем ID:int автоматически
	table_structure = [("ID", "int")]

	# Проверка типов
	for col in columns:
		if ":" not in col:
			print(f"Некорректное значение: {col}. Попробуйте снова.")
			return metadata
		name, type_ = col.split(":", 1)
		if type_ not in VALID_TYPES:
			print(f"Некорректный тип: {type_}. Поддерживаются только "
			      f"{', '.join(VALID_TYPES)}.")
			return metadata
		table_structure.append((name, type_))

	metadata[table_name] = {col: typ for col, typ in table_structure}
	print(f'Таблица "{table_name}" успешно создана со столбцами: ' +
	      ", ".join(f"{k}:{v}" for k, v in metadata[table_name].items()))
	return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
	"""
	Удаляет информацию о таблице из метаданных, если такая была

	:param:
	    metadata: (dict) метаданные
		table_name: (str) имя таблицы
	:return:
		(dict) обновленные метаданные
	"""
	if table_name not in metadata:
		print(f'Ошибка: Таблица "{table_name}" не существует.')
		return metadata

	del metadata[table_name]
	print(f'Таблица "{table_name}" успешно удалена.')
	return metadata

def list_tables(metadata: dict) -> None:
	"""
	Выводит список всех таблиц.

	:param
		metadata: (dict) словарь метаданных
	:return:
	"""
	if not metadata:
		print("Нет созданных таблиц.")
		return
	print("Список таблиц:")
	for table in metadata.keys():
		print(f"- {table}")
# TODO перепроверить CRUD, чтобы все условия выполнял и не было избыточной сложности
def insert(metadata: dict, table_name: str, values: list[str]) -> None:
	"""
	Если таблица существует и количество переданных значений соответствует числу
	столбцов - валидирует типы данных как в схеме в метаданных и добавляет запись.

	:param metadata: (dict) метаданные о таблице
	:param table_name: (str) имя таблицы
	:param values: (list[str]) добавляемые значения
	:return: None
	"""
	if table_name not in metadata:
		print(f'Ошибка: Таблица "{table_name}" не существует.')
		return

	table_schema = metadata[table_name]
	columns = list(table_schema.keys())[1:]  # пропускаем ID
	if len(values) != len(columns):
		print("Ошибка: количество значений не совпадает с количеством столбцов.")
		return

	data = load_table_data(table_name)
	new_id = max((row["ID"] for row in data), default=0) + 1

	record = {"ID": new_id}
	for col, val in zip(columns, values):
		expected_type = table_schema[col]
		try:
			if expected_type == "int":
				val = int(val)
			elif expected_type == "bool":
				val = val.lower() == "true"
			elif expected_type == "str":
				val = str(val).strip('"').strip("'")
		except Exception:
			print(f"Ошибка: некорректное значение {val} для {col}:{expected_type}.")
			return
		record[col] = val

	data.append(record)
	save_table_data(table_name, data)
	print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

def select(table_data: list[dict], where_clause: dict | None = None) -> list[dict]:
	"""
	Возвращает записи из таблицы по условию.

	:param table_data: список всех записей таблицы
	:param where_clause: условие выборки, например {"age": 28}
	:return: список отфильтрованных записей
	"""
	if not table_data:
		print("Нет данных для отображения.")
		return []

	if where_clause:
		col, val = next(iter(where_clause.items()))
		filtered = [row for row in table_data if str(row.get(col)) == str(val)]
	else:
		filtered = table_data

	if not filtered:
		print("Нет записей, удовлетворяющих условию.")
		return []

	table = PrettyTable()
	table.field_names = table_data[0].keys()
	for row in filtered:
		table.add_row([row.get(col, "") for col in table.field_names])
	print(table)

	return filtered

def update(table_data: list[dict], set_clause: dict[str, Any],
           where_clause: dict[str, Any],) -> list[dict]:
	"""
	Обновляет записи в таблице по условию.

	:param table_data: список записей таблицы
	:param set_clause: изменения, например {"age": 29}
	:param where_clause: условие выборки, например {"name": "Sergei"}
	:return: обновлённый список записей
	"""
	col_where, val_where = next(iter(where_clause.items()))
	updated = False

	for row in table_data:
		if str(row.get(col_where)) == str(val_where):
			for key, new_val in set_clause.items():
				if key not in row:
					print(f"Ошибка: столбца '{key}' не существует.")
					return table_data
				try:
					row[key] = type(row[key])(new_val)
				except Exception:
					print(f"Ошибка преобразования типа для поля '{key}'.")
					return table_data
			print(f'Запись с ID={row["ID"]} успешно обновлена.')
			updated = True

	if not updated:
		print("Подходящих записей не найдено.")

	return table_data

def delete(table_data: list[dict], where_clause: dict[str, Any]) -> list[dict]:
	"""
	Удаляет записи из таблицы по условию.

	:param table_data: список записей таблицы
	:param where_clause: условие удаления, например {"ID": 1}
	:return: обновлённый список записей
	"""
	col_where, val_where = next(iter(where_clause.items()))
	new_data: list[dict] = [r for r in table_data if str(r.get(col_where)) != str(val_where)]

	if len(new_data) == len(table_data):
		print("Записей для удаления не найдено.")
	else:
		print(f"Удалено {len(table_data) - len(new_data)} записей из таблицы.")

	return new_data

def info(metadata, table_name):
	if table_name not in metadata:
		print(f'Ошибка: Таблица "{table_name}" не существует.')
		return

	data = load_table_data(table_name)
	print(f"Таблица: {table_name}")
	print("Столбцы:", ", ".join(f"{k}:{v}" for k, v in metadata[table_name].items()))
	print(f"Количество записей: {len(data)}")

def info(metadata: dict, table_name: str) -> None:
	"""
	Выводит информацию о структуре таблицы и количестве записей.

	:param metadata: словарь метаданных проекта
	:param table_name: имя таблицы
	"""
	if table_name not in metadata:
		print(f'Ошибка: Таблица "{table_name}" не существует.')
		return

	from src.primitive_db.utils import load_table_data

	data: list[dict] = load_table_data(table_name)
	print(f"Таблица: {table_name}")
	print("Столбцы:", ", ".join(f"{k}:{v}" for k, v in metadata[table_name].items()))
	print(f"Количество записей: {len(data)}")