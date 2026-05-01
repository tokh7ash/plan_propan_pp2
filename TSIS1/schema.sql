-- ============================================================
-- schema.sql — PhoneBook Practice 9
-- Таблицы и структура БД
-- ============================================================

-- Базовая таблица контактов (Practice 7)
CREATE TABLE IF NOT EXISTS contacts (
    id        SERIAL PRIMARY KEY,
    username  VARCHAR(100) NOT NULL UNIQUE,
    phone     VARCHAR(20)  NOT NULL
);

-- Группы контактов (Practice 9)
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Стандартные группы
INSERT INTO groups (name)
VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- Расширение таблицы contacts (Practice 9)
ALTER TABLE contacts
    ADD COLUMN IF NOT EXISTS email    VARCHAR(100),
    ADD COLUMN IF NOT EXISTS birthday DATE,
    ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES groups(id);

-- Дополнительные номера телефонов (Practice 9)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);
