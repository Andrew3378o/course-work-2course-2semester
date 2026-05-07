import os
from flask import Flask, render_template, abort
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
            cursor.execute("SELECT id, title, content FROM articles LIMIT 10")
            articles = cursor.fetchall()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
    return render_template('index.html', articles=articles)

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    conn = get_db_connection()
    article = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
            article = cursor.fetchone()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    if article is None:
        abort(404)
        
    return render_template('article.html', article=article)

if __name__ == '__main__':
    app.run(debug=True)