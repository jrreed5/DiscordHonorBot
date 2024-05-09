from flask import Flask, render_template
from utils.database import Database
import sqlite3
import json

app = Flask(__name__)

# Replace with your secret key for session management
app.secret_key = 'your_secret_key_here'

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

@app.route('/')
async def leaderboard():
    try:
        # Create a new SQLite connection
        conn = create_connection("database.db")
        cursor = conn.cursor()

        # Fetch members and their total honor from the database
        cursor.execute("SELECT members, guild_id FROM guilds")
        rows = cursor.fetchall()

        members = []
        for row in rows:
            guild_members = json.loads(row[0])
            for member in guild_members:
                total_honor = await get_total_honor(row[1], member["id"], cursor)
                members.append({"name": member["name"], "total_honor": total_honor})

        # Sort members by total honor in descending order
        sorted_members = sorted(members, key=lambda x: x.get("total_honor", 0), reverse=True)

        # Pass the enumerate function to the template environment
        env = app.jinja_env
        env.globals['enumerate'] = enumerate

        return render_template('leaderboard.html', members=sorted_members)

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

async def get_total_honor(guild_id, member_id, cursor):
    """Calculate total honor (high honor + low honor word counts) for a member in a guild"""
    cursor.execute("SELECT members FROM guilds WHERE guild_id = ?", (guild_id,))
    row = cursor.fetchone()
    if row:
        members = json.loads(row[0])
        for member in members:
            if member["id"] == member_id:
                high_honor_count = member.get("high_honor_word_count", 0)
                low_honor_count = member.get("low_honor_word_count", 0)
                # Return the sum of high honor count and negation of low honor count
                return high_honor_count + (-low_honor_count)
    return 0


if __name__ == '__main__':
    app.run(debug=True)
