import psycopg2

# Database connection details
conn = psycopg2.connect(
    dbname="mydb",
    user="your_username",
    password="your_password",
    host="localhost",
    port="5432"
)

# Create a cursor object
cur = conn.cursor()

# SQL query to insert dummy data into the debate_scores table
sql_query = """
INSERT INTO debate_scores (username, user_scores, ai_scores, plot_json)
VALUES 
('Kartik-here', '{70, 80, 75}', '{65, 85, 70}', '{"data": [{"x": [1, 2, 3], "y": [70, 80, 75], "type": "scatter", "name": "User Score"}, {"x": [1, 2, 3], "y": [65, 85, 70], "type": "scatter", "name": "AI Score"}], "layout": {"title": "Debate Scores", "xaxis": {"title": "Rounds"}, "yaxis": {"title": "Score"}}}'),
('Kartik-here', '{85, 90, 95}', '{80, 92, 88}', '{"data": [{"x": [1, 2, 3], "y": [85, 90, 95], "type": "scatter", "name": "User Score"}, {"x": [1, 2, 3], "y": [80, 92, 88], "type": "scatter", "name": "AI Score"}], "layout": {"title": "Debate Scores", "xaxis": {"title": "Rounds"}, "yaxis": {"title": "Score"}}}');
"""

try:
    # Execute the SQL query to insert data
    cur.execute(sql_query)
    # Commit the transaction
    conn.commit()

    print("Dummy data inserted successfully!")

except Exception as e:
    # Rollback in case of any error
    conn.rollback()
    print(f"Error: {e}")

finally:
    # Close the cursor and connection
    cur.close()
    conn.close()
