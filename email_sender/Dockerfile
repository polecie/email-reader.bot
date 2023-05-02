## Базовый образ для сборки
FROM python:3.10-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

# Указываем рабочую директорию
WORKDIR /usr/src/app
ENV PYTHONPATH /usr/src/app/email_sender

# Запрещаем Python писать файлы .pyc на диск
ENV PYTHONDONTWRITEBYTECODE 1
# Запрещает Python буферизовать stdout и stderr
ENV PYTHONUNBUFFERED 1

# Установка зависимостей проекта
COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

# Устанавливаем make
RUN apt-get update && apt-get install -y make

# Устанавливаем playwright
RUN playwright install firefox
RUN apt-get install -y libgtk-3-0  \
    libasound2  \
    libxcomposite1  \
    libxdamage1  \
    libxext6  \
    libxfixes3  \
    libxrandr2  \
    libxrender1  \
    libxtst6  \
    libpangocairo-1.0-0  \
    libpango-1.0-0  \
    libatk1.0-0  \
    libcairo-gobject2  \
    libcairo2  \
    libgdk-pixbuf-2.0-0  \
    libglib2.0-0  \
    libdbus-glib-1-2  \
    libdbus-1-3  \
    libxcb-shm0  \
    libx11-xcb1  \
    libxcursor1  \
    libxi6

# Копируем проект
COPY . .
