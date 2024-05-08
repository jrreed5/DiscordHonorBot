from flaskapp import Flask, render_template
import sqlite3

# Fetch SQLite database file path
db_file_path = "database.db"

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def ranking():
    # Connect to the database
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Retrieve member information from the database
    cursor.execute("SELECT guild_id, members FROM guilds")
    rows = cursor.fetchall()

    # Calculate total honor for each member and store in a list of tuples
    member_honors = []
    for row in rows:
        guild_id, members_json = row
        members = json.loads(members_json)
        for member in members:
            total_honor = sum(member.get("high_honor_word_count", 0) + (-member.get("low_honor_word_count", 0)))
            member_honors.append((guild_id, member["id"], member["name"], total_honor))

    # Sort members based on total honor
    sorted_members = sorted(member_honors, key=lambda x: x[3], reverse=True)

    # Close database connection
    conn.close()

    # Render the ranking page with the sorted member list
    return render_template('ranking.html', members=sorted_members)

if __name__ == '__main__':
    app.run(debug=True)