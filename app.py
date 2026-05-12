import os
import re
from flask import Flask, render_template, abort, request, redirect, url_for, flash
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
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    articles = []
    total_pages = 1
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT COUNT(*) as count FROM articles")
            total_articles = cursor.fetchone()['count']
            total_pages = (total_articles + per_page - 1) // per_page

            query = """
                SELECT a.id, a.title, a.content_markdown, c.name as category_name 
                FROM articles a 
                LEFT JOIN categories c ON a.category_id = c.id 
                ORDER BY a.id DESC 
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (per_page, offset))
            articles = cursor.fetchall()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('index.html', articles=articles, page=page, total_pages=total_pages)

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    conn = get_db_connection()
    article = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT a.*, c.name as category_name 
                FROM articles a 
                LEFT JOIN categories c ON a.category_id = c.id 
                WHERE a.id = %s
            """, (article_id,))
            article = cursor.fetchone()
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    if article is None:
        abort(404)
        
    # Заміна [[Назва статті]] на HTML-посилання
    raw_content = article['content_markdown']
    wiki_link_pattern = r'\[\[(.*?)\]\]'
    processed_content = re.sub(wiki_link_pattern, r'<a href="/wiki/\1" class="wiki-link">\1</a>', raw_content)

    # Конвертація Markdown із підтримкою змісту (toc)
    md = markdown2.Markdown(extras=['break-on-newline', 'cuddled-lists', 'tables', 'fenced-code-blocks', 'toc'])
    html_result = md.convert(processed_content)
    
    article['html_content'] = html_result
    article['toc'] = html_result.toc_html if hasattr(html_result, 'toc_html') and html_result.toc_html else None
    
    return render_template('article.html', article=article)

@app.route('/wiki/<title>')
def wiki_link(title):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id FROM articles WHERE title = %s", (title,))
            article = cursor.fetchone()
            if article:
                return redirect(url_for('article_detail', article_id=article['id']))
            else:
                flash(f'Стаття "{title}" ще не існує. Ви можете створити її першим!', 'info')
                return redirect(url_for('create_article', prefill_title=title))
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('index'))

@app.route('/article/new', methods=['GET', 'POST'])
def create_article():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content_markdown = request.form.get('content_markdown')
        category_id = request.form.get('category_id')

        if title and content_markdown:
            if conn:
                try:
                    cursor.execute(
                        "INSERT INTO articles (title, content_markdown, category_id) VALUES (%s, %s, %s)", 
                        (title, content_markdown, category_id if category_id else None)
                    )
                    conn.commit()
                    flash('Article published successfully!', 'success')
                except Exception as e:
                    flash('Error publishing article.', 'error')
                finally:
                    cursor.close()
                    conn.close()
            return redirect(url_for('index'))
            
    cursor.execute("SELECT * FROM categories ORDER BY name ASC")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    
    prefill_title = request.args.get('prefill_title', '')
    return render_template('create_article.html', categories=categories, prefill_title=prefill_title)

@app.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
def edit_article(article_id):
    conn = get_db_connection()
    if not conn:
        abort(500)
        
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content_markdown = request.form.get('content_markdown')
        category_id = request.form.get('category_id')
        
        if title and content_markdown:
            try:
                cursor.execute(
                    "UPDATE articles SET title = %s, content_markdown = %s, category_id = %s WHERE id = %s", 
                    (title, content_markdown, category_id if category_id else None, article_id)
                )
                conn.commit()
                flash('Article updated successfully!', 'success')
            except Exception as e:
                flash('Error updating article.', 'error')
            finally:
                cursor.close()
                conn.close()
            return redirect(url_for('article_detail', article_id=article_id))
            
    try:
        cursor.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
        article = cursor.fetchone()
        cursor.execute("SELECT * FROM categories ORDER BY name ASC")
        categories = cursor.fetchall()
    except Exception as e:
        article = None
        categories = []
    finally:
        cursor.close()
        conn.close()
        
    if article is None:
        abort(404)
        
    return render_template('edit_article.html', article=article, categories=categories)

@app.route('/article/<int:article_id>/delete', methods=['POST'])
def delete_article(article_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM articles WHERE id = %s", (article_id,))
            conn.commit()
            flash('Article deleted.', 'info')
        except Exception as e:
            flash('Error deleting article.', 'error')
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
            cursor.execute("""
                SELECT a.id, a.title, a.content_markdown, c.name as category_name 
                FROM articles a 
                LEFT JOIN categories c ON a.category_id = c.id 
                WHERE a.title LIKE %s OR a.content_markdown LIKE %s 
                ORDER BY a.id DESC
            """, (search_term, search_term))
            articles = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()
    return render_template('search_results.html', articles=articles, query=query)

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    conn = get_db_connection()
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        if name and name.strip():
            clean_name = name.strip().capitalize()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO categories (name) VALUES (%s)", (clean_name,))
                    conn.commit()
                    flash('Category added successfully!', 'success')
                except Exception:
                    error = "Така категорія вже існує."
                finally:
                    cursor.close()
        else:
            error = "Назва не може бути порожньою."

    categories = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories ORDER BY name ASC")
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('manage_categories.html', categories=categories, error=error)

@app.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
def edit_category(id):
    conn = get_db_connection()
    if request.method == 'POST':
        new_name = request.form.get('name')
        if new_name and new_name.strip():
            clean_name = new_name.strip().capitalize()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("UPDATE categories SET name = %s WHERE id = %s", (clean_name, id))
                    conn.commit()
                    flash('Category updated.', 'success')
                    return redirect(url_for('manage_categories'))
                except Exception as e:
                    flash('Error updating category.', 'error')
                finally:
                    cursor.close()
                    conn.close()
    
    category = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories WHERE id = %s", (id,))
        category = cursor.fetchone()
        cursor.close()
        conn.close()
    
    if not category:
        abort(404)
    return render_template('edit_category.html', category=category)

@app.route('/categories/<int:id>/delete', methods=['POST'])
def delete_category(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM categories WHERE id = %s", (id,))
            conn.commit()
            flash('Category deleted.', 'info')
        except Exception as e:
            flash('Error deleting category.', 'error')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('manage_categories'))

if __name__ == '__main__':
    app.run(debug=True)