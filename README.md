# Проект «Конвертер валют»
___

## Функциональные возможности
---
Данный сервис имеет следующие функциональные возможности:
- Конвертер валют из одной в другую
- Просмотр данных о курсе валют на сегодняшний день
- Получения графика динамики изменения курса валюты
- Просмотр данных о валюте по стране
- Аутентификация пользователя

## Компоненты сервиса
---
Сервис состоит из следующих компонентов:
- Сервис для получения информации о валютах
- Парсер информации о курсе валют на следующий день
- Keycloak
- PostgreSQL

## Как запустить
---
### Инструкция
1. В корневом каталоге проекта создать файл .env со структурой, описаной в соответствующем разделе.
2. Запустить команду `docker compose up keycloak -d`.
3. Перейти на страницу localhost:9000 и авторизоваться в системе.
4. Перейти в Clients -> backend -> Credentials и напротив поля Client Secret нажать Regenerate. 
Полученный секрет скопировать в .env в поле `KEYCLOAK_CLIENT_SECRET`
5. Перейти в Clients -> admin -> Credentials и напротив поля Client Secret нажать Regenerate. 
Полученный секрет скопировать в .env в поле `KEYCLOAK_ADMIN_SECRET`
6. Перейти в Users и нажать на Create new user. Поле Required user actions оставить пустым, Email verificated - on.
Указываем все поля и нажимаем Create
7. Переходим в созданного пользователя, и в нём во вкладку Credentials и задаём пароль, не забывая убрать Temporary.
Нажимаем Save.
8. Вводим `docker compose up -d`
### Файл конфигурации
---
В конфигурации приведены данные для тестирования. Чтобы получить токен DaData, необходимо зарегистрироваться на сайте dadata.ru
В личном кабинете можно будет найти API токен. Без этого токена сервис не запустится.
```shell
# Database
DB_DRIVER=postgresql+asyncpg
DB_HOST=database
DB_USERNAME=localuser
DB_PASSWORD=localpassword
DB_NAME=local_db
DB_PORT=5432

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_PUBLIC_PORT=8080
BACKEND_URI=http://backend:8000/api

# DaData
DADATA_API_TOKEN=

# Keycloak
KEYCLOAK_ADMIN_USER=keycloakuser
KEYCLOAK_ADMIN_PASSWORD=keycloakpassword
KEYCLOAK_URI=http://keycloak:8080/
KEYCLOAK_PUBLIC_URI=http://localhost/auth/
KEYCLOAK_CLIENT_ID=backend
KEYCLOAK_CLIENT_SECRET=
KEYCLOAK_ADMIN_ID=admin
KEYCLOAK_ADMIN_SECRET=
KEYCLOAK_REALM_NAME=demo

# NGINX
DOMAIN=localhost
```

## Стек технологий
---
- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Keycloak
- NGINX