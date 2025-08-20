# csv_to_sqlite.py
import sqlite3
import csv

DB_FILE = "leetcode.db"
CSV_FILE = "leetcode_problems.csv"

def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Drop old tables if they exist
    cur.execute("DROP TABLE IF EXISTS problems;")
    cur.execute("DROP TABLE IF EXISTS user_progress;")

    # Problems table (static directory)
    cur.execute("""
        CREATE TABLE problems (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            url TEXT NOT NULL
        );
    """)

    # User progress table (dynamic)
    cur.execute("""
        CREATE TABLE user_progress (
            user_id TEXT NOT NULL,
            problem_id INTEGER NOT NULL,
            status TEXT CHECK(status IN ('in-progress', 'solved')) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, problem_id),
            FOREIGN KEY(problem_id) REFERENCES problems(id)
        );
    """)

    conn.commit()
    conn.close()

def load_csv_to_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        problems = [
            (int(row["id"]), row["title"], row["difficulty"], row["url"])
            for row in reader
        ]

    cur.executemany(
        "INSERT INTO problems (id, title, difficulty, url) VALUES (?, ?, ?, ?);",
        problems,
    )

    conn.commit()
    conn.close()
    print(f"✅ Loaded {len(problems)} problems into {DB_FILE}")

if __name__ == "__main__":
    create_tables()
    load_csv_to_db()
