import psycopg2
import csv

conn = psycopg2.connect(
    host="37.151.88.186",
    port="59003",
    database="parsers",
    user="parsers",
    password="avrhggfxDJWf827D"
)

cursor = conn.cursor()

# получить все таблицы
cursor.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
""")

tables = cursor.fetchall()

for table in tables:
    table_name = table[0]

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # получить названия колонок
    colnames = [desc[0] for desc in cursor.description]

    with open(f"{table_name}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(colnames)  # заголовки
        writer.writerows(rows)     # данные

    print(f"Таблица {table_name} выгружена")

cursor.close()
conn.close()