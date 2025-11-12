import time
from functools import wraps
from typing import Any, Callable


def handle_db_errors(func: Callable) -> Callable:
	"""
	Декоратор для централизованной обработки ошибок при работе с БД.

	Оборачивает функцию в блок try-except, перехватывает и выводит сообщения
	для типичных исключений: FileNotFoundError, KeyError, ValueError и других.
	"""
	@wraps(func)
	def wrapper(*args: Any, **kwargs: Any) -> Any:
		try:
			return func(*args, **kwargs)
		except FileNotFoundError:
			print("Ошибка: файл данных не найден. Возможно, база данных "
																"не инициализирована.")
		except KeyError as e:
			print(f"Ошибка: таблица или столбец '{e}' не найден.")
		except ValueError as e:
			print(f"Ошибка валидации: {e}")
		except Exception as e:
			print(f"Произошла непредвиденная ошибка: {e}")
		return None
	return wrapper


def confirm_action(action_name: str) -> Callable:
	"""
	Декоратор-фабрика, запрашивающий подтверждение перед выполнением операции.

	:param action_name: человекочитаемое описание действия (например,"удалить таблицу")
	"""
	def decorator(func: Callable) -> Callable:
		@wraps(func)
		def wrapper(*args: Any, **kwargs: Any) -> Any:
			answer = (input(f'Вы уверены, что хотите "{action_name}"? [y/n]: ').strip()
                                                                            .lower())
			if answer != "y":
				print("Операция отменена пользователем.")
				if args:
					first_arg = args[0]
					if isinstance(first_arg, (dict, list)):
						return first_arg
				return None
			return func(*args, **kwargs)
		return wrapper
	return decorator


def log_time(func: Callable) -> Callable:
	"""
	Декоратор, замеряющий время выполнения функции.

	Выводит сообщение вида:
	Функция <имя_функции> выполнилась за X.XXX секунд.
	"""
	@wraps(func)
	def wrapper(*args: Any, **kwargs: Any) -> Any:
		start = time.monotonic()
		result = func(*args, **kwargs)
		elapsed = time.monotonic() - start
		print(f"Функция '{func.__name__}' выполнилась за {elapsed:.3f} секунд.")
		return result
	return wrapper


def create_cacher() -> Callable[[str, Callable[[], Any]], Any]:
	"""
	Функция-замыкание, реализующая кэширование результатов.

	Возвращает внутреннюю функцию cache_result(key, value_func),
	которая проверяет наличие результата в кэше по ключу.
	Если значение есть — возвращает его.
	Если нет — вызывает value_func(), сохраняет результат и возвращает его.
	"""
	cache = {}

	def cache_result(key: str, value_func: Callable[[], Any]) -> Any:
		if key in cache:
			print(f"[КЭШ] Используется сохранённый результат для ключа: '{key}'")
			return cache[key]
		result = value_func()
		cache[key] = result
		return result

	def clear_cache() -> None:
		"""Очищает весь кэш."""
		cache.clear()
		print("[КЭШ] Очищен.")

	cache_result.clear_cache = clear_cache

	return cache_result
