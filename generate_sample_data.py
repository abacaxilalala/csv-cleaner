"""
generate_sample_data.py
-----------------------
Generates a realistic, intentionally messy sales CSV for demonstration.

Messiness included:
  - Missing values in multiple columns
  - Inconsistent date formats
  - Mixed case / extra whitespace in text fields
  - Duplicate rows
  - Invalid numeric values (negative prices, impossible quantities)
  - Inconsistent country names (e.g. "spain", "SPAIN", "España")
  - Mixed currency symbols left in numeric fields
"""

import csv
import random
import os

random.seed(42)

PRODUCTS = [
    "Wireless Headphones", "USB-C Hub", "Laptop Stand", "Mechanical Keyboard",
    "Webcam HD", "Monitor Light", "Mouse Pad XL", "Cable Organiser"
]

CATEGORIES = ["Electronics", "Accessories", "Peripherals", "electronics", "ACCESSORIES"]

COUNTRIES = [
    "Spain", "SPAIN", "spain", "España",
    "Germany", "germany", "GERMANY",
    "France", "france",
    "Italy", "ITALY",
    "Netherlands"
]

DATE_FORMATS = [
    "2024-01-{:02d}",
    "{:02d}/01/2024",
    "January {:02d}, 2024",
    "2024/01/{:02d}"
]

SALES_REPS = [
    "  Ana García", "ANA GARCIA", "ana garcia",
    "Tom Müller", "TOM MULLER", "tom müller  ",
    "Lucia Rossi", "lucia rossi",
    "Jan de Vries", "JAN DE VRIES"
]

def generate_row(row_id: int) -> list:
    product = random.choice(PRODUCTS)
    quantity = random.randint(1, 50)
    unit_price = round(random.uniform(9.99, 299.99), 2)

    # Introduce messiness
    if random.random() < 0.08:
        quantity = random.randint(-5, -1)           # Invalid: negative quantity
    if random.random() < 0.06:
        unit_price_str = f"${unit_price}"           # Currency symbol left in
    elif random.random() < 0.05:
        unit_price_str = ""                         # Missing price
    else:
        unit_price_str = str(unit_price)

    if random.random() < 0.07:
        quantity_str = ""                           # Missing quantity
    else:
        quantity_str = str(quantity)

    date_fmt = random.choice(DATE_FORMATS)
    day = random.randint(1, 28)
    date_str = date_fmt.format(day)

    if random.random() < 0.05:
        date_str = ""                               # Missing date

    country = random.choice(COUNTRIES)
    category = random.choice(CATEGORIES)
    sales_rep = random.choice(SALES_REPS)

    if random.random() < 0.06:
        sales_rep = ""                              # Missing sales rep

    email = f"{sales_rep.strip().lower().replace(' ', '.').replace('á','a').replace('ü','u')}@company.com"
    if random.random() < 0.05:
        email = "not-an-email"                      # Invalid email
    if random.random() < 0.04:
        email = ""                                  # Missing email

    return [
        row_id, product, category, quantity_str, unit_price_str,
        date_str, country, sales_rep, email
    ]


def main():
    output_path = os.path.join(
        os.path.dirname(__file__), "data", "raw", "sales_data_raw.csv"
    )

    header = [
        "order_id", "product", "category", "quantity",
        "unit_price", "order_date", "country", "sales_rep", "email"
    ]

    rows = [generate_row(i) for i in range(1001, 1201)]

    # Inject ~10 duplicate rows
    duplicates = random.sample(rows, 10)
    rows.extend(duplicates)
    random.shuffle(rows)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows → {output_path}")


if __name__ == "__main__":
    main()
