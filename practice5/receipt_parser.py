#!/usr/bin/env python3
"""
receipt_parser.py
Парсер чеков (регулярные выражения).

Использование (Windows / Linux):
  python receipt_parser.py raw.txt
или
  python receipt_parser.py "C:\путь\до\raw.txt"

Если кодировка файла не UTF-8, скрипт попробует cp1251.
Результаты: <имя_файла>.parsed.json, <имя_файла>.parsed.csv, <имя_файла>.pretty.txt
"""
import re
import json
import sys
import csv
from pathlib import Path
from typing import Optional

# Регулярки
AMOUNT_RE = re.compile(r"[\d\s\u00A0]+[.,]\d{2}")  # захватывает "1 200,00" "1200,00" "1200.00"
DATETIME_RE = re.compile(
    r"Время:\s*([0-3]?\d\.[0-1]?\d\.[0-9]{4}\s+[0-2]?\d:[0-5]?\d:[0-5]?\d)"
)
QUANTITY_X_RE = re.compile(r"([\d\s.,]+)\s*x", re.IGNORECASE)
UNIT_PRICE_X_RE = re.compile(r"x\s*([\d\s\u00A0]+[.,]\d{2})", re.IGNORECASE)


def try_read_text(path: Path) -> str:
    """Прочитать текст: сначала UTF-8, если UnicodeDecodeError -> cp1251."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="cp1251")
        except Exception as e:
            raise e


def parse_amount(s: str) -> Optional[float]:
    """Преобразовать '1 200,00' или '1200.00' в float (1200.0)."""
    if s is None:
        return None
    s = str(s).strip()
    s = s.replace("\u00A0", " ")  # NBSP -> space
    s = s.replace(" ", "")        # убрать разделители тысяч
    s = s.replace(",", ".")      # заменить запятую на точку
    try:
        return float(s)
    except Exception:
        return None


def extract_items(lines):
    """Извлечь список товаров: name, quantity, unit_price, total_price."""
    items = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        # начало позиции: "1." "2." ...
        if re.match(r"^\d+\.$", line):
            name_lines = []
            j = i + 1
            # собираем название до строки с 'x' или до следующего номера
            while j < n and not re.search(r"\bx\b", lines[j], re.IGNORECASE):
                if re.match(r"^\d+\.$", lines[j].strip()):
                    break
                name_lines.append(lines[j].strip())
                j += 1

            qty = None
            unit_price = None
            total_price = None

            # если нашлась строка с 'x'
            if j < n and re.search(r"\bx\b", lines[j], re.IGNORECASE):
                xline = lines[j]
                m_unit = UNIT_PRICE_X_RE.search(xline)
                if m_unit:
                    unit_price = parse_amount(m_unit.group(1))
                m_qty = QUANTITY_X_RE.search(xline)
                if m_qty:
                    qty = parse_amount(m_qty.group(1))
                # часто итог позиции на следующей строке
                if j + 1 < n and AMOUNT_RE.search(lines[j + 1]):
                    total_price = parse_amount(AMOUNT_RE.search(lines[j + 1]).group(0))
            else:
                # fallback: ищем первые две суммы в следующих строках
                found = []
                for k in range(i + 1, min(n, i + 7)):
                    m = AMOUNT_RE.search(lines[k])
                    if m:
                        found.append(parse_amount(m.group(0)))
                        if len(found) >= 2:
                            break
                if found:
                    unit_price = found[0]
                    if len(found) > 1 and found[1] != unit_price:
                        total_price = found[1]

            # ещё бывает "Стоимость" и затем сумма
            if j + 2 < n and lines[j + 1].strip().lower().startswith("стоимость") and AMOUNT_RE.search(lines[j + 2]):
                total_price = parse_amount(AMOUNT_RE.search(lines[j + 2]).group(0))

            name = " ".join([ln for ln in name_lines if ln and not ln.lower().startswith("стоимость")]).strip()
            if name:
                items.append(
                    {
                        "name": name,
                        "quantity": qty,
                        "unit_price": unit_price,
                        "total_price": total_price,
                    }
                )
            i = j + 1
        else:
            i += 1
    return items


def parse_receipt_text(text: str) -> dict:
    """Основной парсинг — возвращает словарь с items, total, date_time, payment_method, raw_text."""
    lines = [ln.rstrip("\n") for ln in text.splitlines()]
    items = extract_items(lines)

    all_prices = [parse_amount(m.group(0)) for m in AMOUNT_RE.finditer(text)]
    all_prices = [p for p in all_prices if p is not None]

    # ищем ИТОГО
    total = None
    for idx, ln in enumerate(lines):
        if re.match(r"^\s*ИТОГО:?", ln, re.IGNORECASE):
            if idx + 1 < len(lines) and AMOUNT_RE.search(lines[idx + 1]):
                total = parse_amount(AMOUNT_RE.search(lines[idx + 1]).group(0))
            else:
                m = AMOUNT_RE.search(ln)
                if m:
                    total = parse_amount(m.group(0))
    # fallback: максимальная сумма
    if total is None and all_prices:
        total = max(all_prices)

    # дата/время
    dt = None
    m = DATETIME_RE.search(text)
    if m:
        dt = m.group(1)

    # способ оплаты
    payment_method = None
    for idx, ln in enumerate(lines):
        if "Банковская карта" in ln:
            payment_value = None
            if idx + 1 < len(lines) and AMOUNT_RE.search(lines[idx + 1]):
                payment_value = parse_amount(AMOUNT_RE.search(lines[idx + 1]).group(0))
            payment_method = {"method": "Банковская карта", "amount": payment_value}
            break
        if re.search(r"Наличные", ln, re.IGNORECASE):
            payment_method = {"method": "Наличные"}
            break

    return {
        "items": items,
        "all_prices": all_prices,
        "total": total,
        "date_time": dt,
        "payment_method": payment_method,
        "raw_text": text,
    }


def save_pretty_text(path: Path, raw_text: str):
    """Сохранить красивый текстовый файл с реальными переводами строк."""
    out = path.with_suffix(".pretty.txt")
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    out.write_text(normalized, encoding="utf-8")
    return out


def save_csv(path: Path, items):
    """
    Сохранить CSV для Excel.
    - delimiter=';' для русской локали Excel (чтобы столбцы шли отдельно)
    - encoding='utf-8-sig' чтобы Excel сразу распознал UTF-8
    """
    out = path.with_suffix(".parsed.csv")
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["name", "quantity", "unit_price", "total_price"])
        for it in items:
            writer.writerow(
                [
                    it.get("name", ""),
                    "" if it.get("quantity") is None else it.get("quantity"),
                    "" if it.get("unit_price") is None else "{:.2f}".format(it.get("unit_price")),
                    "" if it.get("total_price") is None else "{:.2f}".format(it.get("total_price")),
                ]
            )
    return out


if __name__ == "__main__":
    path_arg = sys.argv[1] if len(sys.argv) > 1 else "raw.txt"
    p = Path(path_arg)

    print("Текущая папка:", Path.cwd())
    print("Ищу файл:", p.resolve())
    if not p.exists():
        print(f"File not found: {p}")
        sys.exit(1)

    try:
        text = try_read_text(p)
    except Exception as e:
        print("Не удалось прочитать файл:", e)
        sys.exit(1)

    parsed = parse_receipt_text(text)

    out_json = p.with_suffix(".parsed.json")
    try:
        out_json.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print("Ошибка записи JSON:", e)
        sys.exit(1)

    pretty = save_pretty_text(p, parsed["raw_text"])
    csvf = save_csv(p, parsed["items"])

    print("Saved JSON:", out_json)
    print("Pretty text:", pretty)
    print("CSV:", csvf)
    # короткий вывод в консоль
    print(json.dumps(parsed, ensure_ascii=False, indent=2))