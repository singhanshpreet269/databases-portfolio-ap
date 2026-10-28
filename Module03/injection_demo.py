"""Demonstrate SQL injection and its one correct fix: bound parameters."""
import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("warehouse.db")
if not DB.exists():
    raise SystemExit(f"{DB} not found — run the Module 3 setup first")

conn = sqlite3.connect(DB)


def vulnerable(name: str):
    """DON'T DO THIS. String-building the query is the bug."""
    sql = f"SELECT customer_id, name FROM customer WHERE name = '{name}'"
    return conn.execute(sql).fetchall()


def safe(name: str):
    """DO THIS. The value can never be parsed as SQL."""
    sql = "SELECT customer_id, name FROM customer WHERE name = ?"
    return conn.execute(sql, (name,)).fetchall()


if __name__ == "__main__":
    print("normal   :", vulnerable("Customer 1"))

    # 1) The support agent's crash: an ordinary apostrophe in a name
    try:
        print("O'Brien  :", vulnerable("O'Brien"))
    except sqlite3.Error as e:
        print("O'Brien  : crashed with", e)
    print("O'Brien (safe):", safe("O'Brien"))

    # 2) The classic payload: returns ALL rows instead of none
    payload = "' OR '1'='1"
    try:
        rows = vulnerable(payload)
        print("injected :", len(rows), "rows leaked, e.g.", rows[:3], "...")
    except sqlite3.Error as e:
        print("injected : crashed with", e)
    print("safe     :", safe(payload))

    # 3) UNION: read a different table through the same hole
    union = "x' UNION SELECT product_id, sku FROM product WHERE '1'='1"
    try:
        print("union    :", vulnerable(union)[:3], "...")
    except sqlite3.Error as e:
        print("union    : crashed with", e)
    print("union safe:", safe(union))