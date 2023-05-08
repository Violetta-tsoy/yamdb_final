# CI и CD проекта api_yamdb

![Deploy badge](https://github.com/Violetta-tsoy/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

##  Описание проекта:
В проекте yamdb_final настроены Continuous Integration и Continuous Deployment для приложения api_yamdb:

- автоматический запуск тестов,
- обновление образов на Docker Hub,
- автоматический деплой на боевой сервер при пуше в главную ветку master.

Приложение api_yamdb собирает отзывы пользователей о произведениях, которые делятся на категории, такие как «Книги», «Фильмы», «Музыка». 
Произведению может быть присвоен жанр из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). 
Проект запущен по адресу: http://158.160.19.166/api/v1/


## Технологии
- Python 3.9.10
- Django 2.2.16
- Django Rest Framework 3.12.4
- Python
- Docker 20.10.24
- Gunicorn 20.0.4
- Nginx 1.21.3

## Инструкции по запуску:
Склонируйте репозиторий:
```
git clone https://github.com/Violetta-tsoy/yamdb_final.git
```
Войдите на свой удаленный сервер в облаке.
Остановите службу nginx:
```
sudo systemctl stop nginx 
```
Установите docker:
```
sudo apt install docker.io 
```
Установите docker-compose, с этим вам поможет официальная документация: https://docs.docker.com/compose/install/

Скопируйте файлы docker-compose.yaml и nginx/default.conf из вашего проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно.

Добавьте в Secrets GitHub Actions переменные окружения для работы базы данных.
```
SECRET_KEY=<secret key django проекта>
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_NAME=postgres
DB_PASSWORD=postgres
DB_PORT=5432
DB_USER=postgres

DOCKER_PASSWORD=<Docker password>
DOCKER_USERNAME=<Docker username>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ(cat ~/.ssh/id_rsa)>

TG_CHAT_ID=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
```
## Примеры:
Для просмотра документации с примерами перейдите по адресу:
http://158.160.19.166/redoc/