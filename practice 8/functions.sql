CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE(id INT, username VARCHAR, phone VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
        SELECT c.id, c.username, c.phone
        FROM   contacts c
        WHERE  c.username ILIKE '%' || pattern || '%'
           OR  c.phone    ILIKE '%' || pattern || '%'
        ORDER BY c.username;
END;
$$;


CREATE OR REPLACE FUNCTION get_contacts_page(page_size INT, page_num INT)
RETURNS TABLE(id INT, username VARCHAR, phone VARCHAR)
LANGUAGE plpgsql
AS $$
DECLARE
    v_offset INT;
BEGIN
    IF page_size <= 0 THEN
        RAISE EXCEPTION 'page_size must be a positive integer, got %', page_size;
    END IF;
    IF page_num <= 0 THEN
        RAISE EXCEPTION 'page_num must be a positive integer (1-based), got %', page_num;
    END IF;

    v_offset := (page_num - 1) * page_size;

    RETURN QUERY
        SELECT c.id, c.username, c.phone
        FROM   contacts c
        ORDER BY c.username
        LIMIT  page_size
        OFFSET v_offset;
END;
$$;
