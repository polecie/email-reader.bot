import time

from api.models import Mail, TrackedMailSender, User

STATE_AUTH = "AUTH"
MAIL_FOLDER = "all_mails"


def timeit(func):
    """Декоратор для замера скорости работы функций"""

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time() - start
        print(func.__name__, ": ", end)
        return result

    return wrapper


def get_data_by_tg_id(tg_id: int) -> dict:
    """
    Функция-адаптер для получения из бд, преобразования данных и передачи их в MailService
    """
    user = User.objects.filter(tg_id=tg_id).only("id").first()
    q_mails = Mail.objects.select_related("provider").filter(user_id=user.id)
    q_senders = TrackedMailSender.objects.filter(user_id=user.id).values("email")
    return {
        "mails": [mail.to_json() for mail in q_mails],
        "senders": [item["email"] for item in q_senders],
    }
