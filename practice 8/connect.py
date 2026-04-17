import psycopg2
from config import DB_CONFIG


def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn


def create_table():
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:

                # Таблица
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id        SERIAL PRIMARY KEY,
                        username  VARCHAR(100) NOT NULL UNIQUE,
                        phone     VARCHAR(20)  NOT NULL
                    );
                """)

                # Функция search_contacts
                cur.execute("""
                    CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
                    RETURNS TABLE(id INT, username VARCHAR, phone VARCHAR)
                    LANGUAGE plpgsql AS $$
                    BEGIN
                        RETURN QUERY
                            SELECT c.id, c.username, c.phone
                            FROM contacts c
                            WHERE c.username ILIKE '%' || pattern || '%'
                               OR c.phone    ILIKE '%' || pattern || '%'
                            ORDER BY c.username;
                    END; $$;
                """)

                # Функция get_contacts_page
                cur.execute("""
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
                            FROM contacts c
                            ORDER BY c.username
                            LIMIT page_size OFFSET v_offset;
                    END; $$;
                """)

                # Процедура upsert_contact
                cur.execute("""
                    CREATE OR REPLACE PROCEDURE upsert_contact(p_username VARCHAR, p_phone VARCHAR)
                    LANGUAGE plpgsql AS $$
                    BEGIN
                        INSERT INTO contacts (username, phone)
                        VALUES (p_username, p_phone)
                        ON CONFLICT (username) DO UPDATE SET phone = EXCLUDED.phone;
                    END; $$;
                """)

                # Процедура delete_contact
                cur.execute("""
                    CREATE OR REPLACE PROCEDURE delete_contact(
                        p_username VARCHAR DEFAULT NULL,
                        p_phone    VARCHAR DEFAULT NULL
                    )
                    LANGUAGE plpgsql AS $$
                    BEGIN
                        DELETE FROM contacts
                        WHERE (p_username IS NOT NULL AND username = p_username)
                           OR (p_phone    IS NOT NULL AND phone    = p_phone);
                    END; $$;
                """)

        print("[OK] Table and functions/procedures are ready.")
    except Exception as e:
        print(f"[ERROR] Could not create table: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        conn = get_connection()
        print(f"[OK] Connected to PostgreSQL: {DB_CONFIG['dbname']}@{DB_CONFIG['host']}")
        conn.close()
        create_table()
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")