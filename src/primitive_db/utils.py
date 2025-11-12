import json

from src.primitive_db.constants import DATA_DIR


def load_metadata(filepath: str) -> dict:
	'''
	Загружает метаданные из JSON. Если файл не найден - возвращает пустой словарь

	:param
		filepath: (str) путь до целевого JSON-файла
	:return:
		(dict) словарь со считанными из json данными, либо пустой
	'''
	try:
		with open(filepath, 'r', encoding="utf-8") as f:
			return json.load(f)
	except FileNotFoundError:
		return {}
	except json.JSONDecodeError:
		print("Ошибка: поврежден файл метаданных. Создаю новый.")
		return {}

def save_metadata(filepath: str, data: dict) -> None:
	'''
	Сохраняет метаданные в JSON.

	:param
		filepath: (str) путь до json файла для записи
		data: (dict) словарь с данными для записи

	'''
	with open(filepath, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=4, ensure_ascii=False)

def load_table_data(table_name: str) -> list[dict]:
	"""
	Загружает данные таблицы из JSON. Если файл отсутствует, возвращает пустой список.

	:param:
		table_name: (str) имя таблицы для загрузки
	:return:
		(list[dict]) словарь с данными из целевой таблицы
	"""
	filepath = DATA_DIR / f"{table_name}.json"
	try:
		with open(filepath, "r", encoding="utf-8") as f:
			return json.load(f)
	except FileNotFoundError:
		return []
	except json.JSONDecodeError:
		print(f"Ошибка: поврежден файл данных {filepath}. Создаю новый.")
		return []

def save_table_data(table_name: str, data: list[dict]) -> None:
	"""
	Сохраняет данные таблицы в JSON.

	:param:
		table_name: (str) имя таблицы для сохранения
		data: (list[dict]) данные таблицы
	:return:
		None
	"""
	DATA_DIR.mkdir(exist_ok=True)
	filepath = DATA_DIR / f"{table_name}.json"

	with open(filepath, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=4, ensure_ascii=False)