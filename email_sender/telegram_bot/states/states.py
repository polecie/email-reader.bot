from aiogram.dispatcher.filters.state import State, StatesGroup


class AskCreds(StatesGroup):
    """
    Группа состояний для процесса привязки почты
    """

    waiting_for_email = State()
    ask_password = State()


class AskSender(StatesGroup):
    """
    Группа состояний для процесса привязки отправителя
    """

    ask_email = State()


class ListChoiceWait(StatesGroup):
    """
    Группа состояний для процесса выбора элемента списка
    """

    element_choice = State()
