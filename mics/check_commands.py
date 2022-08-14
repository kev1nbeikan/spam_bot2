from data.strings import CommandsAnnotationsS



def check_args_in_command_go(args) -> str | None:
    """
    Проверяет валидность аргументов. None - ошибок нет

    :param args:
    :return:
    """
    if len(args) < 2:
        return f"В аргументах команды 'go' чего-то не хватает. Требуемые аргументы {CommandsAnnotationsS.GO}"

    elif len(args) >= 2:

        if not args[0].isdigit():
            return "Первый аргумент команды 'go' должен быть числом"

        if not args[1].isdigit():
            return "Второй аргумент команды 'go' должен быть числом"

    if len(args) >= 3:
        if not args[2].isdigit():
            return "Третий аргумент команды 'go' должен быть числом"

    return None


def check_args_in_command_join_and_sending(args):
    """
        Проверяет валидность аргументов. None - ошибок нет

        :param args:
        :return:
        """
    if len(args) < 4:
        return f"В аргументах команды 'go' чего-то не хватает. Требуемые аргументы {CommandsAnnotationsS.JOIN_AND_SENDING}"

    elif len(args) >= 4:

        if not args[0].isdigit():
            return "Первый аргумент команды 'go' должен быть числом"

        if not args[1].isdigit():
            return "Второй аргумент команды 'go' должен быть числом"

        if not args[2].isdigit():
            return "Третий аргумент команды 'go' должен быть числом"


    if len(args) >= 3:
        if not args[2].isdigit():
            return "Четвертый аргумент команды 'go' должен быть числом"

    return None