import os
from flask import Flask, render_template, abort, request, redirect, url_for
from dotenv import load_dotenv
from db import get_db_connection

# Initialize environment and app
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')
load_dotenv(env_path, override=True)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')

@app.route('/')
def index():
    conn = get_db_connection()
    articles = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, title, content_markdown FROM articles ORDER BY id DESC LIMIT 10")
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

@app.route('/article/new', methods=['GET', 'POST'])
def create_article():
    if request.method == 'POST':
        title = request.form.get('title')
        content_markdown = request.form.get('content_markdown')

        if title and content_markdown:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO articles (title, content_markdown) VALUES (%s, %s)", (title, content_markdown))
                    conn.commit()
                except Exception as e:
                    print(f"Database error: {e}")
                finally:
                    cursor.close()
                    conn.close()
            return redirect(url_for('index'))
            
    return render_template('create_article.html')

# NEW ROUTE: Edit existing article
@app.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
def edit_article(article_id):
    conn = get_db_connection()
    if not conn:
        abort(500)
        
    cursor = conn.cursor(dictionary=True)
    
    # Handle form submission
    if request.method == 'POST':
        title = request.form.get('title')
        content_markdown = request.form.get('content_markdown')
        
        if title and content_markdown:
            try:
                # Update the database record
                cursor.execute("UPDATE articles SET title = %s, content_markdown = %s WHERE id = %s", (title, content_markdown, article_id))
                conn.commit()
            except Exception as e:
                print(f"Database error: {e}")
            finally:
                cursor.close()
                conn.close()
            # Redirect back to the updated article page
            return redirect(url_for('article_detail', article_id=article_id))
            
    # Handle GET request: fetch current article to pre-fill the form
    try:
        cursor.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
        article = cursor.fetchone()
    except Exception as e:
        print(f"Database error: {e}")
        article = None
    finally:
        cursor.close()
        conn.close()
        
    if article is None:
        abort(404)
        
    return render_template('edit_article.html', article=article)

if __name__ == '__main__':
    app.run(debug=True)