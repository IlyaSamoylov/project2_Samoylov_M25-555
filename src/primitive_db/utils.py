import json

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