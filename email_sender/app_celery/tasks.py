import datetime
import json

from app_celery.mailsender_service import MailSender
from app_celery.schemes import Mail
from app_celery.services import MailService
from app_celery.utils import get_data_by_tg_id
from django.conf import settings
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from email_sender.celery import celery_app


@celery_app.task(name="get_new_mail")
def get_new_mail(tg_id: int):
    """
    Задача на проверку и получение новых писем, если писем или отправителей нет, то не запускаем.

    :param tg_id: int - telegram_id пользователя
    """
    data = get_data_by_tg_id(tg_id)

    if not data.get("mails") or not data.get("senders"):
        return None

    all_mails: list[Mail] = [Mail(**mail) for mail in data["mails"]]
    mail_service = MailService(
        mails=all_mails,
        senders=data["senders"],
        date=datetime.datetime.now()
        - datetime.timedelta(hours=settings.DELTA_HOURS_CHECK_MAIL),
        timeout=settings.IMAP_TIMEOUT_SEC,
        send_method=MailSender(user_id=tg_id),
    )
    mail_service.run()

    if mail_service.get_errors:
        return mail_service.get_errors

    return mail_service.errors


def create_periodic_task(tg_id: int) -> None:
    """
    Функция для создания периодической задачи get_new_mail по tg_id пользователя.

    :param tg_id: int - telegram_id пользователя
    """
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=settings.DEFAULT_PERIOD_TASKS_MIN,
        period=IntervalSchedule.MINUTES,
    )
    PeriodicTask.objects.create(
        interval=schedule,
        name=f"Get_mails_tg_id:{tg_id}",
        task="get_new_mail",
        kwargs=json.dumps({"tg_id": tg_id}),
        start_time=datetime.datetime.utcnow(),
    )
