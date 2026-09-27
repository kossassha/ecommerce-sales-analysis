from pathlib import Path
import sqlite3

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

RAW = ROOT / "data" / "raw"

DB = ROOT / "data" / "ecommerce.db"


tables = {
    "customers": "customers.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv",
}


with sqlite3.connect(DB) as connection:

    for table_name, file_name in tables.items():

        dataframe = pd.read_csv(
            RAW / file_name
        )

        dataframe.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False,
        )

        print(
            f"{table_name}: {len(dataframe)} rows"
        )


print(
    f"Database created: {DB}"
)