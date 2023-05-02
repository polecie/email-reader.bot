THIS_FILE := $(lastword $(MAKEFILE_LIST))
.PHONY: help migrate_and_run createsuperuser
include .env.dev
help:
	make -pRrq  -f $(THIS_FILE) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
migrate_and_run:
	python $(EMAIL_SENDER_DIR)/manage.py makemigrations
	python $(EMAIL_SENDER_DIR)/manage.py migrate
	python $(EMAIL_SENDER_DIR)/manage.py loaddata $(EMAIL_SENDER_DIR)/fixtures/providers.json
	celery --workdir email_sender -A email_sender -q worker --detach
	celery --workdir email_sender -A email_sender beat --detach --scheduler django_celery_beat.schedulers:DatabaseScheduler
	uvicorn email_sender.asgi:application --lifespan=off --host 0.0.0.0 --port 8000 --app-dir $(EMAIL_SENDER_DIR)
createsuperuser:
	python $(EMAIL_SENDER_DIR)/manage.py createsuperuser --noinput
run_django_tests:
	python $(EMAIL_SENDER_DIR)/manage.py test --k
run_bot_tests:
	pytest --disable-pytest-warnings -vv
