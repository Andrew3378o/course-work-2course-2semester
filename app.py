import os
from flask import Flask, render_template
from dotenv import load_dotenv
from db import get_db_connection

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')

@app.route('/')
def index():
    conn = get_db_connection()
    articles = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM articles LIMIT 10")
            articles = cursor.fetchall()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()

    return render_template('index.html', articles=articles)

if __name__ == '__main__':
    app.run(debug=True)