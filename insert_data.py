import json
import mysql.connector

# Load JSON file
with open("questions.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Connect to MySQL Workbench
conn = mysql.connector.connect(
    host="localhost",
    user="root",  # Change this to your MySQL username
    password="yjh434ctuG@-@",  # Change this to your MySQL password
    database="testing_feud"
)
cursor = conn.cursor()

# Insert data into MySQL
for item in data:
    question_text = item["question"]

    # Insert question and get its ID
    cursor.execute("INSERT INTO questions (question_text) VALUES (%s)", (question_text,))
    question_id = cursor.lastrowid  # Get the ID of the inserted question

    # Insert answers linked to this question
    for answer, points in zip(item["answers"], item["points"]):
        cursor.execute("INSERT INTO answers (question_id, answer_text, points) VALUES (%s, %s, %s)",
                       (question_id, answer, points))

# Commit and close
conn.commit()
cursor.close()
conn.close()
print("✅ Data inserted successfully into MySQL!")
