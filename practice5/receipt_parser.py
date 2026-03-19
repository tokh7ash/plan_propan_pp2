import re
import json

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

all_prices = re.findall(r'\b\d[\d\s]*,\d{2}\b', text)
all_prices_clean = [p.replace(" ", "") for p in all_prices]
print("=" * 50)
print("1. ВСЕ ЦЕНЫ В ЧЕКЕ:")
print(", ".join(all_prices_clean))


item_pattern = re.compile(
    r'^\d+\.\s*\n(.+?)\n[\d,]+ x ',
    re.MULTILINE | re.DOTALL
)
names = [m.group(1).replace("\n", " ").strip() for m in item_pattern.finditer(text)]

print("\n" + "=" * 50)
print("2. НАЗВАНИЯ ТОВАРОВ:")
for i, name in enumerate(names, 1):
    print(f"  {i:2}. {name}")


full_pattern = re.compile(
    r'(\d+)\.\s*\n(.+?)\n([\d,]+) x ([\d\s]+,\d{2})\n([\d\s]+,\d{2})',
    re.DOTALL
)

items = []
for m in full_pattern.finditer(text):
    idx      = int(m.group(1))
    name     = m.group(2).replace("\n", " ").strip()
    qty      = float(m.group(3).replace(",", "."))
    price    = float(m.group(4).replace(" ", "").replace(",", "."))
    subtotal = float(m.group(5).replace(" ", "").replace(",", "."))
    items.append({
        "id": idx,
        "name": name,
        "qty": qty,
        "price": price,
        "subtotal": subtotal
    })


dt_match = re.search(r'Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})', text)
date = dt_match.group(1) if dt_match else "не найдено"
time = dt_match.group(2) if dt_match else "не найдено"

print("\n" + "=" * 50)
print("4. ДАТА И ВРЕМЯ:")
print(f"  Дата: {date}")
print(f"  Время: {time}")


payment_match = re.search(r'(Банковская карта|Наличные|Безналичные):\s*\n?([\d\s]+,\d{2})', text)
payment_method = payment_match.group(1) if payment_match else "не найдено"
payment_amount = payment_match.group(2).replace(" ", "") if payment_match else "0"

print("\n" + "=" * 50)
print("5. СПОСОБ ОПЛАТЫ:")
print(f"  {payment_method}: {payment_amount} ₸")


calculated_total = sum(item["subtotal"] for item in items)
total_match = re.search(r'ИТОГО:\s*\n?([\d\s]+,\d{2})', text)
receipt_total = float(total_match.group(1).replace(" ", "").replace(",", ".")) if total_match else 0

print("\n" + "=" * 50)
print("3. ИТОГОВАЯ СУММА:")
print(f"  Подсчитано по позициям: {calculated_total:,.2f} ₸".replace(",", " "))
print(f"  Итого в чеке:           {receipt_total:,.2f} ₸".replace(",", " "))
print(f"  Совпадает: {' ДА' if calculated_total == receipt_total else ' НЕТ'}")


vat_match = re.search(r'НДС 12%:\s*\n?([\d\s]+,\d{2})', text)
vat = float(vat_match.group(1).replace(" ", "").replace(",", ".")) if vat_match else 0.0

result = {
    "store":          "Филиал ТОО EUROPHARMA Астана",
    "bin":            "080841000762",
    "receipt_no":     "2331180266",
    "date":           date,
    "time":           time,
    "cashier":        "Аптека 17-1",
    "items":          items,
    "payment_method": payment_method,
    "vat_12_percent": vat,
    "total":          receipt_total
}

output_path = "receipt_parsed.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 50)
print("6.", output_path)
print(json.dumps(result, ensure_ascii=False, indent=2))