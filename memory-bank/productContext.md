# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-09-03 14:12:19 - Log of updates made will be appended as footnotes to the end of this file.

*

## Project Goal

* Телеграм-бот для удобной записи пользователей на различные мероприятия.

## Key Features

### Для пользователей:
*   Просмотр списка мероприятий.
*   Запись и отмена записи на мероприятия.
*   Создание и редактирование своего профиля (ник, уровень, Polemica ID).
*   Просмотр достижений и рейтинга.
*   Получение справочной информации и контактов.

### Для администраторов:
*   Создание, удаление и управление мероприятиями.
*   Управление пользователями (бан/разбан).
*   Управление списком администраторов.
*   Создание рассылок для участников мероприятий.
*   Выгрузка списка записавшихся в Excel-файл.

## Overall Architecture

*   Проект разделен на следующие директории:
    *   `code`: Основная папка с исходным кодом.
        *   `bot`: Логика телеграм-бота (`admin.py`, `user.py`, `keyboards.py`, `config.py`).
        *   `database`: Работа с базой данных (`models.py`, `requests.py`).
            *   Используется `PostgreSQL` с `asyncpg`.
            *   Определены следующие таблицы:
                *   `banned_users`: для заблокированных пользователей.
                *   `users_in_mailing`: для пользователей в рассылке.
                *   `admins`: для администраторов.
                *   `events`: для мероприятий.
                *   `event_singup`: для записей на мероприятия.
                *   `user_profiles`: для профилей пользователей.
    *   `run.py`: Файл для запуска бота.