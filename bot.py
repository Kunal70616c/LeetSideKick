import os
import sqlite3
import pandas as pd
import discord
from discord.ext import commands
from dotenv import load_dotenv
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Load environment variables
load_dotenv(".env")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("⚠️ Missing DISCORD_TOKEN in local.env")

DB_FILE = "leetcode.db"
CSV_FILE = "leetcode_problems.csv"

# ---------------------------
# Database setup
# ---------------------------
def init_db():
    """Initialize DB if problems table does not exist."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Check if problems table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='problems'")
    table_exists = cur.fetchone()

    if not table_exists:
        print("⚡ No problems table found, creating it from CSV...")
        cur.execute("""
        CREATE TABLE problems (
            id INTEGER PRIMARY KEY,
            title TEXT,
            url TEXT,
            difficulty TEXT
        )
        """)
        df = pd.read_csv(CSV_FILE)
        for _, row in df.iterrows():
            cur.execute(
                "INSERT INTO problems (id, title, url, difficulty) VALUES (?, ?, ?, ?)",
                (row["id"], row["title"], row["url"], row["difficulty"])
            )
        conn.commit()
        print(f"✅ Inserted {len(df)} problems into DB.")
    conn.close()


def get_problem_by_id(problem_id: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, title, url, difficulty FROM problems WHERE id = ?", (problem_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "title": row[1], "url": row[2], "difficulty": row[3]}
    return None

# Run DB init on startup
init_db()

# ---------------------------
# Discord bot setup
# ---------------------------
intents = discord.Intents.default()
intents.message_content = True  # needed for commands
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Track solved and in-progress problems (per user)
user_solved = {}
user_inprogress = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command(name="solved")
async def solved(ctx, problem_id: int):
    problem = get_problem_by_id(problem_id)
    if not problem:
        await ctx.send(f"⚠️ Problem with ID {problem_id} not found.")
        return

    user = ctx.author.name
    user_solved.setdefault(user, []).append(problem_id)

    # Remove from inprogress if exists
    if user in user_inprogress and problem_id in user_inprogress[user]:
        user_inprogress[user].remove(problem_id)

    await ctx.send(
        f"🎉 {ctx.author.mention} solved **{problem['title']}** ({problem['difficulty']})!\n🔗 {problem['url']}"
    )

@bot.command(name="inprogress")
async def inprogress(ctx, problem_id: int):
    problem = get_problem_by_id(problem_id)
    if not problem:
        await ctx.send(f"⚠️ Problem with ID {problem_id} not found.")
        return

    user = ctx.author.name
    user_inprogress.setdefault(user, []).append(problem_id)

    await ctx.send(
        f"📝 {ctx.author.mention} started working on **{problem['title']}** ({problem['difficulty']})!\n🔗 {problem['url']}"
    )

@bot.command(name="stats")
async def stats(ctx):
    user = ctx.author.name
    solved = user_solved.get(user, [])
    inprogress = user_inprogress.get(user, [])

    await ctx.send(
        f"📊 {ctx.author.mention} has solved {len(solved)} problems and is working on {len(inprogress)} problems."
    )

@bot.command(name="list")
async def list_problems(ctx):
    user = ctx.author.name
    solved = user_solved.get(user, [])
    inprogress = user_inprogress.get(user, [])

    msg = f"📚 {ctx.author.mention}'s progress:\n\n"

    if solved:
        msg += "**✅ Solved:**\n"
        for pid in solved:
            prob = get_problem_by_id(pid)
            if prob:
                msg += f"- [{prob['title']}]({prob['url']}) ({prob['difficulty']})\n"
    else:
        msg += "✅ No solved problems yet.\n"

    msg += "\n"

    if inprogress:
        msg += "**📝 In Progress:**\n"
        for pid in inprogress:
            prob = get_problem_by_id(pid)
            if prob:
                msg += f"- [{prob['title']}]({prob['url']}) ({prob['difficulty']})\n"
    else:
        msg += "📝 No problems in progress.\n"

    await ctx.send(msg)
    # At the end of bot.py


def run_server():
    server = HTTPServer(("0.0.0.0", 8080), SimpleHTTPRequestHandler)
    print("⚡ Web server running on port 8080")
    server.serve_forever()

threading.Thread(target=run_server).start()


# Run the bot
bot.run(DISCORD_TOKEN)
