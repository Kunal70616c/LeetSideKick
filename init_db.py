import sqlite3
import pandas as pd

DB_FILE = "leetcode.db"
CSV_FILE = "leetcode_problems.csv"

# Connect to SQLite
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Drop old table if exists
cur.execute("DROP TABLE IF EXISTS problems")

# Create table
cur.execute("""
CREATE TABLE problems (
    id INTEGER PRIMARY KEY,
    title TEXT,
    url TEXT,
    difficulty TEXT
)
""")

# Load CSV
df = pd.read_csv(CSV_FILE)

# Insert into DB
for _, row in df.iterrows():
    cur.execute(
        "INSERT INTO problems (id, title, url, difficulty) VALUES (?, ?, ?, ?)",
        (row["id"], row["title"], row["url"], row["difficulty"])
    )

conn.commit()
conn.close()
print(f"✅ Database initialized with {len(df)} problems!")
