import csv
import sys
from connect import get_connection, create_table


def _print_rows(rows):
    if not rows:
        print("  (no results)")
        return
    print(f"  {'ID':<6} {'USERNAME':<25} {'PHONE':<20}")
    print("  " + "-" * 53)
    for row in rows:
        print(f"  {row[0]:<6} {row[1]:<25} {row[2]:<20}")


def search_contacts(pattern: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
            rows = cur.fetchall()
        print(f"\n  Search results for '{pattern}':")
        _print_rows(rows)
    except Exception as e:
        print(f"[ERROR] search_contacts: {e}")
    finally:
        conn.close()


def upsert_contact():
    username = input("  Enter username : ").strip()
    phone    = input("  Enter phone    : ").strip()
    if not username or not phone:
        print("[ERROR] Username and phone cannot be empty.")
        return
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL upsert_contact(%s, %s);", (username, phone))
        print(f"[OK] Contact '{username}' saved.")
    except Exception as e:
        print(f"[ERROR] upsert_contact: {e}")
    finally:
        conn.close()


def insert_many_contacts_from_csv(filepath: str):
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            pairs = [[row["username"].strip(), row["phone"].strip()] for row in reader]
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        return
    except Exception as e:
        print(f"[ERROR] Reading CSV: {e}")
        return

    if not pairs:
        print("[WARN] CSV is empty, nothing to insert.")
        return

    def pg_quote(s):
        return "'" + s.replace("'", "''") + "'"

    inner = ",".join(
        "ARRAY[" + pg_quote(u) + "," + pg_quote(p) + "]"
        for u, p in pairs
    )
    array_literal = f"ARRAY[{inner}]"

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"CALL insert_many_contacts({array_literal});")

        with conn.cursor() as cur:
            cur.execute("SELECT username, phone, reason FROM invalid_contacts_result;")
            bad_rows = cur.fetchall()

        if bad_rows:
            print("\n  [WARN] Invalid rows that were skipped:")
            print(f"  {'USERNAME':<25} {'PHONE':<20} {'REASON'}")
            print("  " + "-" * 65)
            for r in bad_rows:
                print(f"  {r[0]:<25} {r[1]:<20} {r[2]}")
        else:
            print("[OK] All rows were valid and processed.")
    except Exception as e:
        print(f"[ERROR] insert_many_contacts: {e}")
    finally:
        conn.close()


def get_contacts_page(page_size: int = 5, page_num: int = 1):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_contacts_page(%s, %s);",
                (page_size, page_num),
            )
            rows = cur.fetchall()
        print(f"\n  Page {page_num} (size={page_size}):")
        _print_rows(rows)
        if len(rows) == page_size:
            print(f"  → There may be more rows. Try page {page_num + 1}.")
        else:
            print(f"  → Last page (returned {len(rows)} row(s)).")
    except Exception as e:
        print(f"[ERROR] get_contacts_page: {e}")
    finally:
        conn.close()


def delete_contact():
    print("  Leave a field empty to skip it.")
    username = input("  Enter username (or leave blank): ").strip() or None
    phone    = input("  Enter phone    (or leave blank): ").strip() or None

    if not username and not phone:
        print("[ERROR] Provide at least one field.")
        return

    label = username or phone
    confirm = input(f"  Delete contact matching '{label}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "CALL delete_contact(p_username := %s, p_phone := %s);",
                    (username, phone),
                )
        print("[OK] delete_contact procedure executed.")
    except Exception as e:
        print(f"[ERROR] delete_contact: {e}")
    finally:
        conn.close()


def insert_from_csv(filepath):
    sql = """
        INSERT INTO contacts (username, phone)
        VALUES (%s, %s)
        ON CONFLICT (username) DO NOTHING;
    """
    conn = get_connection()
    inserted = 0
    skipped = 0
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [(row["username"].strip(), row["phone"].strip()) for row in reader]
        with conn:
            with conn.cursor() as cur:
                for username, phone in rows:
                    cur.execute(sql, (username, phone))
                    if cur.rowcount:
                        inserted += 1
                    else:
                        skipped += 1
        print(f"[OK] CSV import done — inserted: {inserted}, skipped: {skipped}")
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
    except Exception as e:
        print(f"[ERROR] CSV import failed: {e}")
    finally:
        conn.close()


def show_all():
    sql = "SELECT id, username, phone FROM contacts ORDER BY username;"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        print(f"\n  All contacts ({len(rows)} total):")
        _print_rows(rows)
    except Exception as e:
        print(f"[ERROR] Could not fetch contacts: {e}")
    finally:
        conn.close()


def update_phone_by_username():
    username  = input("  Enter username to update : ").strip()
    new_phone = input("  Enter new phone number   : ").strip()
    if not username or not new_phone:
        print("[ERROR] Fields cannot be empty.")
        return
    sql = "UPDATE contacts SET phone = %s WHERE username = %s;"
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, (new_phone, username))
                if cur.rowcount:
                    print(f"[OK] Phone updated for '{username}'.")
                else:
                    print(f"[WARN] No contact with username '{username}' found.")
    except Exception as e:
        print(f"[ERROR] Update failed: {e}")
    finally:
        conn.close()


def update_username_by_phone():
    phone        = input("  Enter phone to look up    : ").strip()
    new_username = input("  Enter new username        : ").strip()
    if not phone or not new_username:
        print("[ERROR] Fields cannot be empty.")
        return
    sql = "UPDATE contacts SET username = %s WHERE phone = %s;"
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, (new_username, phone))
                if cur.rowcount:
                    print(f"[OK] Username updated for phone '{phone}'.")
                else:
                    print(f"[WARN] No contact with phone '{phone}' found.")
    except Exception as e:
        print(f"[ERROR] Update failed: {e}")
    finally:
        conn.close()


MENU = """
╔══════════════════════════════════════════════╗
║          PhoneBook — Main Menu (P8)          ║
╠══════════════════════════════════════════════╣
║  1.  Show all contacts                       ║
║  2.  Search by name / phone (pattern)        ║
║  3.  Add / update contact (upsert)           ║
║  4.  Import many contacts from CSV (validated)║
║  5.  Import contacts from CSV (simple)       ║
║  6.  Show contacts page by page              ║
║  7.  Update phone (by username)              ║
║  8.  Update username (by phone)              ║
║  9.  Delete contact (by username or phone)   ║
║  0.  Exit                                    ║
╚══════════════════════════════════════════════╝
"""


def main():
    create_table()
    while True:
        print(MENU)
        choice = input("  Your choice: ").strip()

        if choice == "1":
            show_all()
        elif choice == "2":
            pattern = input("  Enter search pattern: ").strip()
            search_contacts(pattern)
        elif choice == "3":
            upsert_contact()
        elif choice == "4":
            filepath = input("  Enter CSV file path [contacts.csv]: ").strip()
            insert_many_contacts_from_csv(filepath or "contacts.csv")
        elif choice == "5":
            filepath = input("  Enter CSV file path [contacts.csv]: ").strip()
            insert_from_csv(filepath or "contacts.csv")
        elif choice == "6":
            try:
                size = int(input("  Page size  [5] : ").strip() or "5")
                page = int(input("  Page number[1] : ").strip() or "1")
            except ValueError:
                print("[ERROR] Please enter valid integers.")
                continue
            get_contacts_page(size, page)
        elif choice == "7":
            update_phone_by_username()
        elif choice == "8":
            update_username_by_phone()
        elif choice == "9":
            delete_contact()
        elif choice == "0":
            print("  Goodbye!")
            sys.exit(0)
        else:
            print("  [WARN] Invalid choice.")


if __name__ == "__main__":
    main()
