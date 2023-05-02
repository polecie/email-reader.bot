from django.urls import path

from .views import mails, senders, users
from .views.mails import MailsListView
from .views.providers import ProvidersListView
from .views.senders import SendersListView

urlpatterns = [
    path(
        "users/",
        users.UsersViewSet.as_view({"get": "retrieve", "post": "create"}),
        name="users_view",
    ),
    path(
        "users/mail/<str:email>/",
        mails.UserMailViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="users_mails_view",
    ),
    path(
        "users/mail_sender/<str:email>/",
        senders.UserMailSendersViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="users_mail_senders_view",
    ),
    path("users/mails/", MailsListView.as_view(), name="users_mails_list_view"),
    path(
        "users/senders/", SendersListView.as_view(), name="users_mail_senders_list_view"
    ),
    path("providers/", ProvidersListView.as_view(), name="providers_list"),
]
