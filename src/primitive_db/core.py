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
