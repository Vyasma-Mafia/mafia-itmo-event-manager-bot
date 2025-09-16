-- Миграция для добавления поля passes_sent в таблицу events
-- Дата: 2025-09-16
-- Описание: Добавляет поле для отслеживания статуса отправки проходок

-- Добавить новое поле в таблицу events
ALTER TABLE events ADD COLUMN passes_sent BOOLEAN DEFAULT FALSE;

-- Обновить существующие записи (по умолчанию проходки не отправлены)
UPDATE events SET passes_sent = FALSE WHERE passes_sent IS NULL;

-- Добавить комментарий к полю для документации
COMMENT ON COLUMN events.passes_sent IS 'Флаг, указывающий, были ли отправлены проходки для мероприятия';