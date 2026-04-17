CREATE OR REPLACE FUNCTION is_valid_phone(phone TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    digits TEXT;
BEGIN
    IF phone ~ '[^0-9 +\-()]' THEN
        RETURN FALSE;
    END IF;
    digits := regexp_replace(phone, '[^0-9]', '', 'g');
    RETURN length(digits) BETWEEN 7 AND 15;
END;
$$;


CREATE OR REPLACE PROCEDURE upsert_contact(
    p_username TEXT,
    p_phone    TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO contacts (username, phone)
    VALUES (p_username, p_phone)
    ON CONFLICT (username)
    DO UPDATE SET phone = EXCLUDED.phone;

    RAISE NOTICE '[OK] upsert_contact: contact "%" saved with phone "%".', p_username, p_phone;
END;
$$;


CREATE OR REPLACE PROCEDURE insert_many_contacts(
    data TEXT[][]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i          INT;
    v_username TEXT;
    v_phone    TEXT;
    inserted   INT := 0;
    skipped    INT := 0;
BEGIN
    DROP TABLE IF EXISTS invalid_contacts_result;
    CREATE TEMP TABLE invalid_contacts_result (
        username TEXT,
        phone    TEXT,
        reason   TEXT
    );

    FOR i IN 1 .. array_length(data, 1) LOOP
        v_username := trim(data[i][1]);
        v_phone    := trim(data[i][2]);

        IF NOT is_valid_phone(v_phone) THEN
            INSERT INTO invalid_contacts_result VALUES
                (v_username, v_phone, 'invalid phone format');
            skipped := skipped + 1;
            CONTINUE;
        END IF;

        INSERT INTO contacts (username, phone)
        VALUES (v_username, v_phone)
        ON CONFLICT (username) DO NOTHING;

        inserted := inserted + 1;
    END LOOP;

    RAISE NOTICE '[OK] insert_many_contacts: inserted=%, skipped(invalid)=%.', inserted, skipped;
END;
$$;


CREATE OR REPLACE PROCEDURE delete_contact(
    p_username TEXT DEFAULT NULL,
    p_phone    TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    rows_deleted INT;
BEGIN
    IF p_username IS NULL AND p_phone IS NULL THEN
        RAISE EXCEPTION 'delete_contact: supply at least one of p_username or p_phone.';
    END IF;

    IF p_username IS NOT NULL AND p_phone IS NOT NULL THEN
        DELETE FROM contacts WHERE username = p_username OR phone = p_phone;
    ELSIF p_username IS NOT NULL THEN
        DELETE FROM contacts WHERE username = p_username;
    ELSE
        DELETE FROM contacts WHERE phone = p_phone;
    END IF;

    GET DIAGNOSTICS rows_deleted = ROW_COUNT;

    IF rows_deleted > 0 THEN
        RAISE NOTICE '[OK] delete_contact: % row(s) deleted.', rows_deleted;
    ELSE
        RAISE NOTICE '[WARN] delete_contact: no matching contact found.';
    END IF;
END;
$$;
