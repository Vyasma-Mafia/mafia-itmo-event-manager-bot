# Decision Log

This file records architectural and implementation decisions using a list format.
2025-09-03 14:12:49 - Log of updates made.

*

## Decision

*

## Rationale 

*

## Implementation Details

*
[2025-09-05 08:21:00] - Регистрация гостей и отправка проходок

## Decision

*   Добавлена возможность регистрации для пользователей, не являющихся студентами/сотрудниками ИТМО.
*   Реализована функция отправки проходок для гостей через POST-запрос на внешний URL.

## Rationale

*   Необходимо было обеспечить возможность участия в мероприятиях для игроков из других клубов и вузов.
*   Автоматизация отправки данных для проходок упрощает работу администраторов и снижает риск ошибок.

## Implementation Details

*   **База данных:**
    *   В модель `UserProfile` ([`code/database/models.py:86`](code/database/models.py:86)) добавлены поля `full_name`, `passport`, `phone`.
    *   В модель `Event` ([`code/gode/database/models.py:56`](code/database/models.py:56)) добавлено поле `guest_limit`.
*   **Логика:**
    *   Расширен сценарий создания/редактирования профиля в [`user.py`](code/bot/user.py:1) для сбора данных гостей.
    *   Внедрена проверка лимита гостей при записи на мероприятие.
    *   Добавлена кнопка "Отправить проходки" и соответствующий хендлер в [`admin.py`](code/bot/admin.py:1) для отправки данных через `httpx`.