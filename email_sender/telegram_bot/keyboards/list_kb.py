from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

list_senders_cb = CallbackData("list_senders")
list_senders_button = InlineKeyboardButton(
    text="Список отправителей", callback_data=list_senders_cb.new()
)

list_mails_cb = CallbackData("list_mails")
list_mails_button = InlineKeyboardButton(
    text="Список email-адресов", callback_data=list_mails_cb.new()
)

list_elem_cb = CallbackData("list_elem", "action", "id", "main_value")
list_service_cb = CallbackData("list_service", "url", sep=" ")

actions_keys = {"list_senders": "email", "list_mails": "email", "link_mail": "name"}


async def create_list_kb(response: dict | None, action: str) -> InlineKeyboardMarkup:
    """
    Генерирует по ответу на запрос списка с пагинацией инлайн клавиатуру с объектами списка
    и сервиснымми кнопками
    """
    if action not in actions_keys or not isinstance(response, dict):
        raise ValueError

    results: list = response.get("results", [])
    page_size = max(len(results), 1)
    list_kb = InlineKeyboardMarkup(row_width=page_size)
    prev = response.get("previous")
    next = response.get("next")

    for object in results:
        id = object.get("id")
        main_value = object.get(actions_keys[action])
        list_kb.insert(
            InlineKeyboardButton(
                text=f"{main_value}",
                callback_data=list_elem_cb.new(
                    action=action, id=id, main_value=main_value
                ),
            )
        )

    if prev is not None:
        list_kb.add(
            InlineKeyboardButton(
                text="Назад", callback_data=list_service_cb.new(url=prev)
            )
        )

    if next is not None:
        list_kb.insert(
            InlineKeyboardButton(
                text="Вперед", callback_data=list_service_cb.new(url=next)
            )
        )

    if action == "link_mail":
        list_kb.add(
            InlineKeyboardButton(
                text="Нет подходящего",
                callback_data=list_elem_cb.new(action=action, id=0, main_value=""),
            )
        )

    # todo добавить кнопку, что провайдер не перечислен, если action(предварительно нужно изменить view и сериализатор)

    return list_kb
