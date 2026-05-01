"""
PhoneBook — Practice 9
Extends Practice 7 & 8 with:
  • Extended schema (groups, phones, email, birthday)
  • Filter by group, search by email, sort results
  • Paginated console navigation (next/prev/quit)
  • Export to JSON / Import from JSON
  • Extended CSV import (email, birthday, group, phone type)
  • Stored procedures: add_phone, move_to_group, search_contacts (extended)
"""

import csv
import json
import sys
from datetime import date, datetime
from connect import get_connection, migrate


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _print_contacts(rows, headers=None):
    """Pretty-print rows. Adapts to actual row width."""
    if not rows:
        print("  (no results)")
        return
    n = len(rows[0])
    default_h = ["ID", "USERNAME", "PHONE", "EMAIL", "BIRTHDAY", "GROUP"]
    if headers is None:
        headers = default_h[:n]
    while len(headers) < n:
        headers.append(f"COL{len(headers)}")
    col_w = [
        max(len(str(headers[i])), max(len(str(r[i] if r[i] is not None else "")) for r in rows))
        for i in range(n)
    ]
    sep = "  " + "-" * (sum(col_w) + 3 * (n - 1) + 2)
    print("  " + "  ".join(str(headers[i]).ljust(col_w[i]) for i in range(n)))
    print(sep)
    for row in rows:
        print("  " + "  ".join(str(row[i] if row[i] is not None else "").ljust(col_w[i])
                                for i in range(n)))


def _get_groups() -> list[tuple]:
    """Return [(id, name), ...]."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM groups ORDER BY name;")
            return cur.fetchall()
    finally:
        conn.close()


def _pick_group(prompt="  Select group (leave blank to skip): ") -> int | None:
    groups = _get_groups()
    print("  Available groups:")
    for gid, gname in groups:
        print(f"    {gid}. {gname}")
    val = input(prompt).strip()
    if not val:
        return None
    try:
        gid = int(val)
        if any(g[0] == gid for g in groups):
            return gid
        print("[WARN] Unknown group id, skipping.")
        return None
    except ValueError:
        # Maybe typed a name
        for gid, gname in groups:
            if gname.lower() == val.lower():
                return gid
        print("[WARN] Group not found, skipping.")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# 3.2  Advanced Search & Filter
# ══════════════════════════════════════════════════════════════════════════════

def search_contacts(pattern: str):
    """Uses the extended PL/pgSQL search_contacts function (P9)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
            rows = cur.fetchall()
        print(f"\n  Search results for '{pattern}':")
        _print_contacts(rows)
    except Exception as e:
        print(f"[ERROR] search_contacts: {e}")
    finally:
        conn.close()


def filter_by_group():
    """Show contacts belonging to a chosen group."""
    group_id = _pick_group("  Select group id: ")
    if group_id is None:
        return

    sort_col = _pick_sort_column()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT c.id, c.username, c.phone, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                WHERE c.group_id = %s
                ORDER BY {sort_col};
            """, (group_id,))
            rows = cur.fetchall()
        print(f"\n  Contacts in selected group ({len(rows)} total):")
        _print_contacts(rows)
    except Exception as e:
        print(f"[ERROR] filter_by_group: {e}")
    finally:
        conn.close()


def search_by_email():
    """Partial match on email field."""
    pattern = input("  Enter email pattern (e.g. gmail): ").strip()
    if not pattern:
        print("[ERROR] Pattern cannot be empty.")
        return
    sort_col = _pick_sort_column()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT c.id, c.username, c.phone, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                WHERE c.email ILIKE %s
                ORDER BY {sort_col};
            """, (f"%{pattern}%",))
            rows = cur.fetchall()
        print(f"\n  Contacts matching email '{pattern}':")
        _print_contacts(rows)
    except Exception as e:
        print(f"[ERROR] search_by_email: {e}")
    finally:
        conn.close()


def _pick_sort_column() -> str:
    """Let user choose sort order; returns safe SQL column expression."""
    print("  Sort by: 1) name  2) birthday  3) date added (id)")
    choice = input("  Sort choice [1]: ").strip() or "1"
    return {"1": "c.username", "2": "c.birthday NULLS LAST", "3": "c.id"}.get(choice, "c.username")


def show_all_sorted():
    """Show all contacts with user-chosen sort."""
    sort_col = _pick_sort_column()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT c.id, c.username, c.phone, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                ORDER BY {sort_col};
            """)
            rows = cur.fetchall()
        print(f"\n  All contacts ({len(rows)} total):")
        _print_contacts(rows)
    except Exception as e:
        print(f"[ERROR] show_all: {e}")
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# 3.2  Paginated console navigation  (next / prev / quit)
# ══════════════════════════════════════════════════════════════════════════════

def browse_pages():
    """Interactive paginator using get_contacts_page() from Practice 8."""
    try:
        page_size = int(input("  Page size [5]: ").strip() or "5")
    except ValueError:
        page_size = 5

    page = 1
    while True:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_contacts_page(%s, %s);", (page_size, page))
                rows = cur.fetchall()
        except Exception as e:
            print(f"[ERROR] Pagination: {e}")
            conn.close()
            break
        finally:
            conn.close()

        print(f"\n  ── Page {page} (size={page_size}) ──")
        # get_contacts_page returns (id, username, phone) — P8 signature kept
        if rows:
            print(f"  {'ID':<6} {'USERNAME':<25} {'PHONE':<20}")
            print("  " + "-" * 53)
            for r in rows:
                print(f"  {r[0]:<6} {r[1]:<25} {r[2]:<20}")
        else:
            print("  (no more results)")

        is_last = len(rows) < page_size
        nav_opts = []
        if page > 1:
            nav_opts.append("prev")
        if not is_last and rows:
            nav_opts.append("next")
        nav_opts.append("quit")
        print(f"  Options: {' / '.join(nav_opts)}")
        cmd = input("  > ").strip().lower()

        if cmd == "next" and "next" in nav_opts:
            page += 1
        elif cmd == "prev" and "prev" in nav_opts:
            page -= 1
        elif cmd == "quit":
            break
        else:
            print("  [WARN] Invalid option.")


# ══════════════════════════════════════════════════════════════════════════════
# 3.3  Export / Import JSON
# ══════════════════════════════════════════════════════════════════════════════

def _date_serial(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Not serializable: {type(obj)}")


def export_to_json():
    filepath = input("  Output JSON file [contacts_export.json]: ").strip() or "contacts_export.json"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.id, c.username, c.phone, c.email,
                    c.birthday, g.name AS group_name,
                    COALESCE(
                        json_agg(
                            json_build_object('phone', ph.phone, 'type', ph.type)
                        ) FILTER (WHERE ph.id IS NOT NULL),
                        '[]'
                    ) AS phones
                FROM contacts c
                LEFT JOIN groups g  ON g.id = c.group_id
                LEFT JOIN phones ph ON ph.contact_id = c.id
                GROUP BY c.id, c.username, c.phone, c.email, c.birthday, g.name
                ORDER BY c.username;
            """)
            rows = cur.fetchall()
            cols = [desc[0] for desc in cur.description]

        contacts = []
        for row in rows:
            d = dict(zip(cols, row))
            # phones already json from db
            if isinstance(d["phones"], str):
                d["phones"] = json.loads(d["phones"])
            contacts.append(d)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2, default=_date_serial)

        print(f"[OK] Exported {len(contacts)} contacts to '{filepath}'.")
    except Exception as e:
        print(f"[ERROR] export_to_json: {e}")
    finally:
        conn.close()


def import_from_json():
    filepath = input("  Input JSON file [contacts_export.json]: ").strip() or "contacts_export.json"
    try:
        with open(filepath, encoding="utf-8") as f:
            contacts = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        return
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        return

    inserted = skipped = overwritten = 0
    conn = get_connection()
    try:
        for c in contacts:
            username = (c.get("username") or "").strip()
            phone    = (c.get("phone") or "").strip()
            email    = c.get("email")
            birthday = c.get("birthday")
            group_name = c.get("group_name")
            phones_list = c.get("phones", [])

            if not username or not phone:
                print(f"[SKIP] Missing username/phone: {c}")
                skipped += 1
                continue

            # Resolve group
            group_id = None
            if group_name:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
                    row = cur.fetchone()
                    if row:
                        group_id = row[0]
                    else:
                        cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id;", (group_name,))
                        group_id = cur.fetchone()[0]
                conn.commit()

            # Check duplicate
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM contacts WHERE username = %s;", (username,))
                existing = cur.fetchone()

            if existing:
                action = input(f"  Contact '{username}' exists. [s]kip / [o]verwrite? ").strip().lower()
                if action != "o":
                    skipped += 1
                    continue
                with conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE contacts
                            SET phone=%s, email=%s, birthday=%s, group_id=%s
                            WHERE username=%s;
                        """, (phone, email, birthday, group_id, username))
                contact_id = existing[0]
                overwritten += 1
            else:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO contacts (username, phone, email, birthday, group_id)
                            VALUES (%s, %s, %s, %s, %s) RETURNING id;
                        """, (username, phone, email, birthday, group_id))
                        contact_id = cur.fetchone()[0]
                inserted += 1

            # Insert extra phones
            for ph in phones_list:
                ph_num  = ph.get("phone", "").strip()
                ph_type = ph.get("type", "mobile")
                if ph_num:
                    with conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO phones (contact_id, phone, type)
                                VALUES (%s, %s, %s)
                                ON CONFLICT DO NOTHING;
                            """, (contact_id, ph_num, ph_type))

        print(f"[OK] JSON import done — inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}")
    except Exception as e:
        print(f"[ERROR] import_from_json: {e}")
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# 3.3  Extended CSV import  (email, birthday, group, phone type)
# ══════════════════════════════════════════════════════════════════════════════

def import_from_csv_extended():
    """
    Extended CSV format (new columns are optional):
      username, phone, email, birthday, group, phone_type
    Falls back gracefully if columns are absent.
    """
    filepath = input("  Enter CSV file path [contacts.csv]: ").strip() or "contacts.csv"
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        return
    except Exception as e:
        print(f"[ERROR] Reading CSV: {e}")
        return

    if not rows:
        print("[WARN] CSV is empty.")
        return

    fieldnames = rows[0].keys()
    inserted = skipped = 0
    conn = get_connection()
    try:
        for row in rows:
            username   = row.get("username", "").strip()
            phone      = row.get("phone", "").strip()
            email      = row.get("email", "").strip() or None
            birthday   = row.get("birthday", "").strip() or None
            group_name = row.get("group", "").strip() or None
            phone_type = row.get("phone_type", "mobile").strip() or "mobile"

            if not username or not phone:
                skipped += 1
                continue

            # Validate phone_type
            if phone_type not in ("home", "work", "mobile"):
                phone_type = "mobile"

            # Validate birthday format
            if birthday:
                try:
                    datetime.strptime(birthday, "%Y-%m-%d")
                except ValueError:
                    birthday = None

            # Resolve group
            group_id = None
            if group_name:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM groups WHERE name ILIKE %s;", (group_name,))
                    g = cur.fetchone()
                    if g:
                        group_id = g[0]
                    else:
                        cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id;", (group_name,))
                        group_id = cur.fetchone()[0]
                conn.commit()

            # Upsert contact
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO contacts (username, phone, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (username) DO UPDATE
                            SET phone    = EXCLUDED.phone,
                                email    = COALESCE(EXCLUDED.email,    contacts.email),
                                birthday = COALESCE(EXCLUDED.birthday, contacts.birthday),
                                group_id = COALESCE(EXCLUDED.group_id, contacts.group_id)
                        RETURNING id;
                    """, (username, phone, email, birthday, group_id))
                    contact_id = cur.fetchone()[0]

            # Add phone to phones table
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO phones (contact_id, phone, type)
                        VALUES (%s, %s, %s);
                    """, (contact_id, phone, phone_type))

            inserted += 1

        print(f"[OK] Extended CSV import done — inserted/updated: {inserted}, skipped: {skipped}")
    except Exception as e:
        print(f"[ERROR] Extended CSV import: {e}")
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# 3.4  Stored procedure wrappers (add_phone, move_to_group)
# ══════════════════════════════════════════════════════════════════════════════

def add_phone_to_contact():
    contact_name = input("  Enter contact username: ").strip()
    phone        = input("  Enter phone number: ").strip()
    print("  Phone type: home / work / mobile")
    phone_type   = input("  Enter type [mobile]: ").strip() or "mobile"
    if not contact_name or not phone:
        print("[ERROR] Fields cannot be empty.")
        return
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL add_phone(%s, %s, %s);", (contact_name, phone, phone_type))
        print(f"[OK] Phone added to '{contact_name}'.")
    except Exception as e:
        print(f"[ERROR] add_phone: {e}")
    finally:
        conn.close()


def move_contact_to_group():
    contact_name = input("  Enter contact username: ").strip()
    group_name   = input("  Enter group name (existing or new): ").strip()
    if not contact_name or not group_name:
        print("[ERROR] Fields cannot be empty.")
        return
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL move_to_group(%s, %s);", (contact_name, group_name))
        print(f"[OK] '{contact_name}' moved to group '{group_name}'.")
    except Exception as e:
        print(f"[ERROR] move_to_group: {e}")
    finally:
        conn.close()


def show_phones_for_contact():
    """Show all phone numbers from the phones table for a contact."""
    username = input("  Enter contact username: ").strip()
    if not username:
        return
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ph.id, ph.phone, ph.type
                FROM phones ph
                JOIN contacts c ON c.id = ph.contact_id
                WHERE c.username = %s
                ORDER BY ph.type;
            """, (username,))
            rows = cur.fetchall()
        print(f"\n  Phones for '{username}':")
        if rows:
            print(f"  {'ID':<6} {'PHONE':<20} {'TYPE'}")
            print("  " + "-" * 36)
            for r in rows:
                print(f"  {r[0]:<6} {r[1]:<20} {r[2]}")
        else:
            print("  (no extra phones recorded)")
    except Exception as e:
        print(f"[ERROR] show_phones: {e}")
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# Practice 8 wrappers kept as-is
# ══════════════════════════════════════════════════════════════════════════════

def upsert_contact():
    username = input("  Enter username : ").strip()
    phone    = input("  Enter phone    : ").strip()
    if not username or not phone:
        print("[ERROR] Fields cannot be empty.")
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


def insert_many_from_csv(filepath: str):
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            pairs = [[row["username"].strip(), row["phone"].strip()] for row in reader]
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        return

    def pg_quote(s):
        return "'" + s.replace("'", "''") + "'"

    inner = ",".join("ARRAY[" + pg_quote(u) + "," + pg_quote(p) + "]" for u, p in pairs)
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"CALL insert_many_contacts(ARRAY[{inner}]);")
        with conn.cursor() as cur:
            cur.execute("SELECT username, phone, reason FROM invalid_contacts_result;")
            bad = cur.fetchall()
        if bad:
            print("\n  [WARN] Invalid rows skipped:")
            for r in bad:
                print(f"    {r[0]} | {r[1]} | {r[2]}")
        else:
            print("[OK] All rows processed.")
    except Exception as e:
        print(f"[ERROR] insert_many_contacts: {e}")
    finally:
        conn.close()


def delete_contact():
    print("  Leave a field blank to skip it.")
    username = input("  Username (or blank): ").strip() or None
    phone    = input("  Phone    (or blank): ").strip() or None
    if not username and not phone:
        print("[ERROR] Provide at least one field.")
        return
    confirm = input(f"  Delete contact matching '{username or phone}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL delete_contact(p_username := %s, p_phone := %s);", (username, phone))
        print("[OK] delete_contact executed.")
    except Exception as e:
        print(f"[ERROR] delete_contact: {e}")
    finally:
        conn.close()


def update_phone_by_username():
    username  = input("  Username to update : ").strip()
    new_phone = input("  New phone number   : ").strip()
    if not username or not new_phone:
        print("[ERROR] Fields cannot be empty.")
        return
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE contacts SET phone=%s WHERE username=%s;", (new_phone, username))
                if cur.rowcount:
                    print(f"[OK] Phone updated for '{username}'.")
                else:
                    print(f"[WARN] No contact '{username}' found.")
    except Exception as e:
        print(f"[ERROR] update_phone: {e}")
    finally:
        conn.close()


def update_username_by_phone():
    phone        = input("  Phone to look up  : ").strip()
    new_username = input("  New username      : ").strip()
    if not phone or not new_username:
        print("[ERROR] Fields cannot be empty.")
        return
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE contacts SET username=%s WHERE phone=%s;", (new_username, phone))
                if cur.rowcount:
                    print(f"[OK] Username updated for phone '{phone}'.")
                else:
                    print(f"[WARN] No contact with phone '{phone}' found.")
    except Exception as e:
        print(f"[ERROR] update_username: {e}")
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# Menu
# ══════════════════════════════════════════════════════════════════════════════

MENU = """
╔══════════════════════════════════════════════════════╗
║           PhoneBook — Practice 9 Main Menu           ║
╠══════════════════════════════════════════════════════╣
║  ── View & Search ──────────────────────────────     ║
║   1. Show all contacts (with sort)                   ║
║   2. Search by name / phone / email (pattern)        ║
║   3. Filter by group                                 ║
║   4. Search by email                                 ║
║   5. Browse pages (next/prev navigation)             ║
║  ── Add / Edit ─────────────────────────────────     ║
║   6. Add / update contact (upsert, P8)               ║
║   7. Add extra phone number to contact               ║
║   8. Move contact to group                           ║
║   9. Update phone (by username)                      ║
║  10. Update username (by phone)                      ║
║  ── Import / Export ────────────────────────────     ║
║  11. Import CSV — basic (P7 style)                   ║
║  12. Import CSV — extended (email/birthday/group)    ║
║  13. Import many from CSV with validation (P8)       ║
║  14. Export all contacts to JSON                     ║
║  15. Import contacts from JSON                       ║
║  ── Delete ──────────────────────────────────────    ║
║  16. Delete contact (by username or phone)           ║
║  ── Info ────────────────────────────────────────    ║
║  17. Show phones for a contact                       ║
║   0. Exit                                            ║
╚══════════════════════════════════════════════════════╝
"""


def insert_from_csv_basic(filepath):
    """Original P7/P8 basic CSV import (username, phone only)."""
    sql = "INSERT INTO contacts (username, phone) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING;"
    conn = get_connection()
    inserted = skipped = 0
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [(r["username"].strip(), r["phone"].strip()) for r in reader]
        with conn:
            with conn.cursor() as cur:
                for u, p in rows:
                    cur.execute(sql, (u, p))
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


def main():
    migrate()
    while True:
        print(MENU)
        choice = input("  Your choice: ").strip()

        if choice == "1":
            show_all_sorted()
        elif choice == "2":
            pattern = input("  Enter search pattern: ").strip()
            search_contacts(pattern)
        elif choice == "3":
            filter_by_group()
        elif choice == "4":
            search_by_email()
        elif choice == "5":
            browse_pages()
        elif choice == "6":
            upsert_contact()
        elif choice == "7":
            add_phone_to_contact()
        elif choice == "8":
            move_contact_to_group()
        elif choice == "9":
            update_phone_by_username()
        elif choice == "10":
            update_username_by_phone()
        elif choice == "11":
            fp = input("  CSV file path [contacts.csv]: ").strip() or "contacts.csv"
            insert_from_csv_basic(fp)
        elif choice == "12":
            import_from_csv_extended()
        elif choice == "13":
            fp = input("  CSV file path [contacts.csv]: ").strip() or "contacts.csv"
            insert_many_from_csv(fp)
        elif choice == "14":
            export_to_json()
        elif choice == "15":
            import_from_json()
        elif choice == "16":
            delete_contact()
        elif choice == "17":
            show_phones_for_contact()
        elif choice == "0":
            print("  Goodbye!")
            sys.exit(0)
        else:
            print("  [WARN] Invalid choice.")


if __name__ == "__main__":
    main()