import os
from flask import Flask, render_template, abort, request, redirect, url_for
from dotenv import load_dotenv
from db import get_db_connection
import markdown2

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
        
    article['html_content'] = markdown2.markdown(
        article['content_markdown'], 
        extras=['break-on-newline', 'cuddled-lists', 'tables', 'fenced-code-blocks']
    )  
    
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

@app.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
def edit_article(article_id):
    conn = get_db_connection()
    if not conn:
        abort(500)
        
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content_markdown = request.form.get('content_markdown')
        
        if title and content_markdown:
            try:
                cursor.execute("UPDATE articles SET title = %s, content_markdown = %s WHERE id = %s", (title, content_markdown, article_id))
                conn.commit()
            except Exception as e:
                print(f"Database error: {e}")
            finally:
                cursor.close()
                conn.close()
            return redirect(url_for('article_detail', article_id=article_id))
            
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

@app.route('/article/<int:article_id>/delete', methods=['POST'])
def delete_article(article_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM articles WHERE id = %s", (article_id,))
            conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    conn = get_db_connection()
    articles = []
    if conn and query:
        cursor = conn.cursor(dictionary=True)
        try:
            search_term = f"%{query}%"
            cursor.execute("SELECT id, title, content_markdown FROM articles WHERE title LIKE %s OR content_markdown LIKE %s ORDER BY id DESC", (search_term, search_term))
            articles = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()
    return render_template('search_results.html', articles=articles, query=query)

if __name__ == '__main__':
    app.run(debug=True)