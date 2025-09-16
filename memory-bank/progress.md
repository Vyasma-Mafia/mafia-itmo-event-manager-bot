# Progress

This file tracks the project's progress using a task list format.
2025-09-03 14:12:40 - Log of updates made.

*

## Completed Tasks

*   

## Current Tasks

*   

## Next Steps

*

[2025-09-16 14:00:35] - Реализация блокировки записи гостей после отправки проходок завершена

## Completed Tasks

*   ✅ Добавлено поле `passes_sent` в модель `Event` ([`models.py:67`](code/database/models.py:67))
*   ✅ Созданы функции `mark_passes_sent()` и `check_passes_sent()` ([`requests.py:354-370`](code/database/requests.py:354-370))
*   ✅ Обновлены импорты в админской панели ([`admin.py:21`](code/bot/admin.py:21))
*   ✅ Добавлена проверка повторной отправки проходок ([`admin.py:485`](code/bot/admin.py:485))
*   ✅ Реализована автоматическая установка флага после отправки ([`admin.py:530`](code/bot/admin.py:530))
*   ✅ Добавлена проверка статуса проходок при записи гостей ([`user.py:426`](code/bot/user.py:426))
*   ✅ Добавлено отображение статуса в информации о мероприятии ([`user.py:302`](code/bot/user.py:302))
*   ✅ Создан SQL-скрипт миграции ([`migration_add_passes_sent.sql`](migration_add_passes_sent.sql))

## Current Tasks

*   Готово к тестированию и развертыванию

## Next Steps

*   Выполнить миграцию базы данных: `psql -d database_name -f migration_add_passes_sent.sql`
*   Протестировать функциональность:
    1. Запись гостей до отправки проходок (должна работать)
    2. Отправка проходок администратором
    3. Попытка записи новых гостей после отправки (должна блокироваться)
    4. Запись студентов ИТМО после отправки проходок (должна работать)