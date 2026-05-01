

-- ── Practice 8 ───────────────────────────────────────────────────────────────

-- Валидация номера телефона
CREATE OR REPLACE FUNCTION is_valid_phone(phone TEXT)
RETURNS BOOLEAN LANGUAGE plpgsql AS $$
DECLARE digits TEXT;
BEGIN
    IF phone ~ '[^0-9 +\-()] ' THEN RETURN FALSE; END IF;
    digits := regexp_replace(phone, '[^0-9]', '', 'g');
    RETURN length(digits) BETWEEN 7 AND 15;
END; $$;


-- Пагинация контактов
CREATE OR REPLACE FUNCTION get_contacts_page(page_size INT, page_num INT)
RETURNS TABLE(id INT, username VARCHAR, phone VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE v_offset INT;
BEGIN
    IF page_size <= 0 THEN RAISE EXCEPTION 'page_size must be positive'; END IF;
    IF page_num  <= 0 THEN RAISE EXCEPTION 'page_num must be positive';  END IF;
    v_offset := (page_num - 1) * page_size;
    RETURN QUERY
        SELECT c.id, c.username, c.phone
        FROM contacts c ORDER BY c.username
        LIMIT page_size OFFSET v_offset;
END; $$;


-- Upsert контакта
CREATE OR REPLACE PROCEDURE upsert_contact(p_username TEXT, p_phone TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO contacts (username, phone)
    VALUES (p_username, p_phone)
    ON CONFLICT (username) DO UPDATE SET phone = EXCLUDED.phone;
END; $$;


-- Массовая вставка с валидацией
CREATE OR REPLACE PROCEDURE insert_many_contacts(data TEXT[][])
LANGUAGE plpgsql AS $$
DECLARE
    i INT; v_username TEXT; v_phone TEXT;
    inserted INT := 0; skipped INT := 0;
BEGIN
    DROP TABLE IF EXISTS invalid_contacts_result;
    CREATE TEMP TABLE invalid_contacts_result (
        username TEXT, phone TEXT, reason TEXT
    );
    FOR i IN 1 .. array_length(data, 1) LOOP
        v_username := trim(data[i][1]);
        v_phone    := trim(data[i][2]);
        IF NOT is_valid_phone(v_phone) THEN
            INSERT INTO invalid_contacts_result
            VALUES (v_username, v_phone, 'invalid phone format');
            skipped := skipped + 1;
            CONTINUE;
        END IF;
        INSERT INTO contacts (username, phone)
        VALUES (v_username, v_phone)
        ON CONFLICT (username) DO NOTHING;
        inserted := inserted + 1;
    END LOOP;
    RAISE NOTICE 'insert_many_contacts: inserted=%, skipped=%.', inserted, skipped;
END; $$;


-- Удаление контакта по username или phone
CREATE OR REPLACE PROCEDURE delete_contact(
    p_username TEXT DEFAULT NULL,
    p_phone    TEXT DEFAULT NULL
) LANGUAGE plpgsql AS $$
DECLARE rows_deleted INT;
BEGIN
    IF p_username IS NULL AND p_phone IS NULL THEN
        RAISE EXCEPTION 'Provide at least one of p_username or p_phone.';
    END IF;
    IF p_username IS NOT NULL AND p_phone IS NOT NULL THEN
        DELETE FROM contacts WHERE username = p_username OR phone = p_phone;
    ELSIF p_username IS NOT NULL THEN
        DELETE FROM contacts WHERE username = p_username;
    ELSE
        DELETE FROM contacts WHERE phone = p_phone;
    END IF;
    GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    RAISE NOTICE 'delete_contact: % row(s) deleted.', rows_deleted;
END; $$;


-- ── Practice 9 ───────────────────────────────────────────────────────────────

-- Расширенный поиск: по username, phone (contacts), email, phone (phones)
DROP FUNCTION IF EXISTS search_contacts(TEXT);
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id       INT,
    username VARCHAR,
    phone    VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
        SELECT DISTINCT
            c.id,
            c.username,
            c.phone,
            c.email,
            c.birthday,
            g.name AS grp
        FROM contacts c
        LEFT JOIN groups g  ON g.id = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        WHERE c.username ILIKE '%' || p_query || '%'
           OR c.phone    ILIKE '%' || p_query || '%'
           OR c.email    ILIKE '%' || p_query || '%'
           OR ph.phone   ILIKE '%' || p_query || '%'
        ORDER BY c.username;
END; $$;


-- Добавление номера в таблицу phones
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
) LANGUAGE plpgsql AS $$
DECLARE v_id INT;
BEGIN
    SELECT id INTO v_id FROM contacts WHERE username = p_contact_name;
    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Phone type must be home / work / mobile, got "%".', p_type;
    END IF;
    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_id, p_phone, p_type);
    RAISE NOTICE 'add_phone: added % (%) to contact "%".', p_phone, p_type, p_contact_name;
END; $$;


-- Перемещение контакта в группу (создаёт группу если не существует)
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
) LANGUAGE plpgsql AS $$
DECLARE v_group_id INT; v_contact_id INT;
BEGIN
    SELECT id INTO v_contact_id FROM contacts WHERE username = p_contact_name;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;
    INSERT INTO groups (name) VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
    RAISE NOTICE 'move_to_group: "%" moved to group "%".', p_contact_name, p_group_name;
END; $$;
