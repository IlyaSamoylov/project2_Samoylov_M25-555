import prompt


def welcome():
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
