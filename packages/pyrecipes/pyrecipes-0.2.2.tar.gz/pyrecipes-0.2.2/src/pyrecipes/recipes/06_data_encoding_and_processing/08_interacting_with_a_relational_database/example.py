"""
You need to select, insert or delete rows in a relational database.
"""
import sqlite3


def main():
    stocks = [
        ("GOOG", 100, 490.1),
        ("AAPL", 50, 545.75),
        ("FB", 150, 7.45),
        ("HPQ", 75, 33.2),
    ]
    print("stocks:", stocks)

    with sqlite3.connect(":memory:") as db:
        print(db)

        c = db.cursor()
        c.execute(
            """
            CREATE TABLE portfolio
            (symbol text,
            shares integer,
            price real)
            """
        )
        db.commit()

        c.executemany(
            """
            INSERT INTO portfolio VALUES (?, ?, ?)
            """,
            stocks,
        )

        for row in db.execute("SELECT * FROM portfolio"):
            print(row)


if __name__ == "__main__":
    main()
