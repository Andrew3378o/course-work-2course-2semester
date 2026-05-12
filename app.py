import os
import re
import uuid
from flask import Flask, render_template, abort, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from db import get_db_connection
import markdown2
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')
load_dotenv(env_path, override=True)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')

app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                    if cursor.fetchone():
                        flash('Username already exists.', 'error')
                    else:
                        hashed_password = generate_password_hash(password)
                        cursor.execute(
                            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                            (username, hashed_password, 'Editor')
                        )
                        conn.commit()
                        flash('Registration successful! Please log in.', 'success')
                        return redirect(url_for('login'))
                except Exception as e:
                    flash('Database error.', 'error')
                finally:
                    cursor.close()
                    conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                    user = cursor.fetchone()
                    
                    if user and check_password_hash(user['password_hash'], password):
                        session['user_id'] = user['id']
                        session['username'] = user['username']
                        session['role'] = user.get('role', '')
                        flash(f'Welcome back, {user["username"]}!', 'success')
                        return redirect(url_for('index'))
                    else:
                        flash('Invalid username or password.', 'error')
                except Exception as e:
                    flash('Database error.', 'error')
                finally:
                    cursor.close()
                    conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

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
            pass
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

            if article:
                cursor.execute("""
                    SELECT t.name 
                    FROM tags t 
                    JOIN article_tags at ON t.id = at.tag_id 
                    WHERE at.article_id = %s
                """, (article_id,))
                article['tags'] = [row['name'] for row in cursor.fetchall()]

        except Exception as e:
            pass
        finally:
            cursor.close()
            conn.close()
    
    if article is None:
        abort(404)
        
    raw_content = article['content_markdown']
    wiki_link_pattern = r'\[\[(.*?)\]\]'
    processed_content = re.sub(wiki_link_pattern, r'<a href="/wiki/\1" class="wiki-link">\1</a>', raw_content)

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
                if 'user_id' in session:
                    flash(f'Стаття "{title}" ще не існує. Ви можете створити її першим!', 'info')
                    return redirect(url_for('create_article', prefill_title=title))
                else:
                    flash(f'Стаття "{title}" не існує. Увійдіть, щоб створити її.', 'info')
                    return redirect(url_for('login'))
        except Exception as e:
            pass
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('index'))

@app.route('/article/new', methods=['GET', 'POST'])
@login_required
def create_article():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content_markdown = request.form.get('content_markdown')
        category_id = request.form.get('category_id')
        tags_string = request.form.get('tags', '')

        if title and content_markdown:
            if conn:
                try:
                    cursor.execute(
                        "INSERT INTO articles (title, content_markdown, category_id) VALUES (%s, %s, %s)", 
                        (title, content_markdown, category_id if category_id else None)
                    )
                    article_id = cursor.lastrowid

                    if tags_string:
                        tag_names = [t.strip() for t in tags_string.split(',') if t.strip()]
                        for t_name in tag_names:
                            cursor.execute("SELECT id FROM tags WHERE name = %s", (t_name,))
                            tag = cursor.fetchone()
                            if not tag:
                                cursor.execute("INSERT INTO tags (name) VALUES (%s)", (t_name,))
                                tag_id = cursor.lastrowid
                            else:
                                tag_id = tag['id']
                            cursor.execute("INSERT INTO article_tags (article_id, tag_id) VALUES (%s, %s)", (article_id, tag_id))

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
@login_required
def edit_article(article_id):
    conn = get_db_connection()
    if not conn:
        abort(500)
        
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content_markdown = request.form.get('content_markdown')
        category_id = request.form.get('category_id')
        tags_string = request.form.get('tags', '')
        
        if title and content_markdown:
            try:
                cursor.execute("SELECT content_markdown FROM articles WHERE id = %s", (article_id,))
                old_data = cursor.fetchone()
                
                if old_data and old_data['content_markdown'] != content_markdown:
                    cursor.execute(
                        "INSERT INTO revisions (article_id, author_id, old_content) VALUES (%s, %s, %s)",
                        (article_id, session.get('user_id'), old_data['content_markdown'])
                    )

                cursor.execute(
                    "UPDATE articles SET title = %s, content_markdown = %s, category_id = %s WHERE id = %s", 
                    (title, content_markdown, category_id if category_id else None, article_id)
                )

                cursor.execute("DELETE FROM article_tags WHERE article_id = %s", (article_id,))
                if tags_string:
                    tag_names = [t.strip() for t in tags_string.split(',') if t.strip()]
                    for t_name in tag_names:
                        cursor.execute("SELECT id FROM tags WHERE name = %s", (t_name,))
                        tag = cursor.fetchone()
                        if not tag:
                            cursor.execute("INSERT INTO tags (name) VALUES (%s)", (t_name,))
                            tag_id = cursor.lastrowid
                        else:
                            tag_id = tag['id']
                        cursor.execute("INSERT INTO article_tags (article_id, tag_id) VALUES (%s, %s)", (article_id, tag_id))

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

        cursor.execute("""
            SELECT t.name 
            FROM tags t 
            JOIN article_tags at ON t.id = at.tag_id 
            WHERE at.article_id = %s
        """, (article_id,))
        current_tags = cursor.fetchall()
        tags_string = ", ".join([t['name'] for t in current_tags])

    except Exception as e:
        article = None
        categories = []
        tags_string = ""
    finally:
        cursor.close()
        conn.close()
        
    if article is None:
        abort(404)
        
    return render_template('edit_article.html', article=article, categories=categories, tags_string=tags_string)

@app.route('/tag/<tag_name>')
def tag_articles(tag_name):
    conn = get_db_connection()
    articles = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT a.id, a.title, a.content_markdown, c.name as category_name 
                FROM articles a 
                JOIN article_tags at ON a.id = at.article_id
                JOIN tags t ON at.tag_id = t.id
                LEFT JOIN categories c ON a.category_id = c.id 
                WHERE t.name = %s
                ORDER BY a.id DESC
            """, (tag_name,))
            articles = cursor.fetchall()
        except Exception as e:
            pass
        finally:
            cursor.close()
            conn.close()
    return render_template('tag_articles.html', articles=articles, tag_name=tag_name)

@app.route('/article/<int:article_id>/history')
def article_history(article_id):
    conn = get_db_connection()
    revisions = []
    article = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, title FROM articles WHERE id = %s", (article_id,))
            article = cursor.fetchone()
            
            if article:
                cursor.execute("""
                    SELECT r.id, r.old_content, r.changed_at, u.username 
                    FROM revisions r 
                    LEFT JOIN users u ON r.author_id = u.id 
                    WHERE r.article_id = %s 
                    ORDER BY r.changed_at DESC
                """, (article_id,))
                revisions = cursor.fetchall()
        except Exception as e:
            pass
        finally:
            cursor.close()
            conn.close()
            
    if not article:
        abort(404)
        
    return render_template('history.html', article=article, revisions=revisions)

@app.route('/article/<int:article_id>/delete', methods=['POST'])
@login_required
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
                SELECT DISTINCT a.id, a.title, a.content_markdown, c.name as category_name 
                FROM articles a 
                LEFT JOIN categories c ON a.category_id = c.id 
                LEFT JOIN article_tags at ON a.id = at.article_id
                LEFT JOIN tags t ON at.tag_id = t.id
                WHERE a.title LIKE %s 
                   OR a.content_markdown LIKE %s 
                   OR t.name LIKE %s
                ORDER BY a.id DESC
            """, (search_term, search_term, search_term))
            articles = cursor.fetchall()
        except Exception as e:
            pass
        finally:
            cursor.close()
            conn.close()
    return render_template('search_results.html', articles=articles, query=query)

@app.route('/categories', methods=['GET', 'POST'])
@login_required
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
                except Exception as e:
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
@login_required
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
@login_required
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

@app.route('/media', methods=['GET', 'POST'])
@login_required
def media_library():
    conn = get_db_connection()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            if not filename:
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"image_{uuid.uuid4().hex[:8]}.{ext}"
                
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO media (filename) VALUES (%s)", (filename,))
                    conn.commit()
                    flash('File uploaded successfully!', 'success')
                except Exception as e:
                    flash(f'Insert Error: {str(e)}', 'error')
                finally:
                    cursor.close()
            return redirect(url_for('media_library'))
        else:
            flash('Invalid file type.', 'error')
            return redirect(url_for('media_library'))
            
    media_files = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM media ORDER BY id DESC")
            media_files = cursor.fetchall()
        except Exception as e:
            flash(f'Select Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
            
    return render_template('media.html', media_files=media_files)

@app.route('/media/<int:media_id>/delete', methods=['POST'])
@login_required
def delete_media(media_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT filename FROM media WHERE id = %s", (media_id,))
            media = cursor.fetchone()
            
            if media:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], media['filename'])
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                cursor.execute("DELETE FROM media WHERE id = %s", (media_id,))
                conn.commit()
                flash('Media file deleted.', 'info')
            else:
                flash('Media not found.', 'error')
        except Exception as e:
            flash(f'Delete Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('media_library'))

if __name__ == '__main__':
    app.run(debug=True)