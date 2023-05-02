from django.contrib import admin

from .models import Mail, MailProvider, TrackedMailSender, User

admin.site.register(Mail)
admin.site.register(MailProvider)
admin.site.register(User)
admin.site.register(TrackedMailSender)
