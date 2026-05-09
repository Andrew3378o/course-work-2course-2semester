import os
from flask import Flask, render_template, abort, request, redirect, url_for
from dotenv import load_dotenv
from db import get_db_connection

# Initialize environment and app
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
            cursor.execute("SELECT id, title, content FROM articles ORDER BY id DESC LIMIT 10")
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

# Route to handle creation of new articles
@app.route('/article/new', methods=['GET', 'POST'])
def create_article():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        # Basic validation
        if title and content:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    # Insert new article into database
                    cursor.execute("INSERT INTO articles (title, content) VALUES (%s, %s)", (title, content))
                    conn.commit()
                except Exception as e:
                    print(f"Database error: {e}")
                finally:
                    cursor.close()
                    conn.close()
            return redirect(url_for('index'))
            
    # Render form for GET requests
    return render_template('create_article.html')

if __name__ == '__main__':
    app.run(debug=True)