import os
import re
import uuid
from flask import Flask, render_template, abort, request, redirect, url_for, flash, session, jsonify
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

def extract_first_image(text):
    if not text:
        return None
    match = re.search(r'!\[.*?\]\((.*?)\)', text)
    if match:
        return match.group(1)
    return None

def generate_snippet(text, max_length=150):
    if not text:
        return ""
    html = markdown2.markdown(text)
    clean_text = re.sub(r'<[^>]+>', '', html)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    if len(clean_text) > max_length:
        return clean_text[:max_length] + '...'
    return clean_text

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'Admin':
            flash('Admin privileges required for this action.', 'error')
            return redirect(request.referrer or url_for('index'))
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
    category_filter = request.args.get('category', type=int)
    per_page = 6
    offset = (page - 1) * per_page
    conn = get_db_connection()
    articles = []
    category_tree = []
    total_pages = 1
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, name, parent_id FROM categories ORDER BY name ASC")
            all_cats = cursor.fetchall()
            for cat in all_cats:
                if cat['parent_id'] is None:
                    cat['subcategories'] = [sub for sub in all_cats if sub['parent_id'] == cat['id']]
                    category_tree.append(cat)
                    
            if category_filter:
                cursor.execute("SELECT COUNT(*) as count FROM articles WHERE category_id = %s", (category_filter,))
            else:
                cursor.execute("SELECT COUNT(*) as count FROM articles")
                
            total_articles = cursor.fetchone()['count']
            total_pages = (total_articles + per_page - 1) // per_page
            
            if category_filter:
                query = """
                    SELECT a.id, a.title, a.content_markdown, c.name as category_name 
                    FROM articles a 
                    LEFT JOIN categories c ON a.category_id = c.id 
                    WHERE a.category_id = %s
                    ORDER BY a.id DESC 
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (category_filter, per_page, offset))
            else:
                query = """
                    SELECT a.id, a.title, a.content_markdown, c.name as category_name 
                    FROM articles a 
                    LEFT JOIN categories c ON a.category_id = c.id 
                    ORDER BY a.id DESC 
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (per_page, offset))
                
            articles = cursor.fetchall()
            for a in articles:
                a['snippet'] = generate_snippet(a['content_markdown'])
                a['thumbnail'] = extract_first_image(a['content_markdown'])
        except Exception as e:
            pass
        finally:
            cursor.close()
            conn.close()
    return render_template('index.html', articles=articles, page=page, total_pages=total_pages, category_tree=category_tree, current_category=category_filter)

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
                    flash(f'Стаття "{title}" ще не існує. Створіть її!', 'info')
                    return redirect(url_for('create_article', prefill_title=title))
                else:
                    flash(f'Стаття "{title}" не існує. Увійдіть для створення.', 'info')
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
    if request.method == 'POST':
        title = request.form.get('title')
        content_markdown = request.form.get('content_markdown')
        category_id = request.form.get('category_id')
        tags_string = request.form.get('tags', '')
        if title and content_markdown:
            if conn:
                cursor = conn.cursor(dictionary=True)
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
                    flash('Article published!', 'success')
                    return redirect(url_for('index'))
                except Exception as e:
                    flash('Error publishing article.', 'error')
                finally:
                    cursor.close()
                    conn.close()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM categories ORDER BY name ASC")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    prefill_title = request.args.get('prefill_title', '')
    return render_template('create_article.html', categories=categories, prefill_title=prefill_title)

@app.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form.get('title')
        content_markdown = request.form.get('content_markdown')
        category_id = request.form.get('category_id')
        tags_string = request.form.get('tags', '')
        if title and content_markdown:
            if conn:
                cursor = conn.cursor(dictionary=True)
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
                    flash('Article updated!', 'success')
                    return redirect(url_for('article_detail', article_id=article_id))
                except Exception as e:
                    flash('Error updating article.', 'error')
                finally:
                    cursor.close()
                    conn.close()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
    article = cursor.fetchone()
    cursor.execute("SELECT id, name FROM categories ORDER BY name ASC")
    categories = cursor.fetchall()
    cursor.execute("""
        SELECT t.name FROM tags t 
        JOIN article_tags at ON t.id = at.tag_id 
        WHERE at.article_id = %s
    """, (article_id,))
    tags_string = ", ".join([t['name'] for t in cursor.fetchall()])
    cursor.close()
    conn.close()
    if not article: abort(404)
    return render_template('edit_article.html', article=article, categories=categories, tags_string=tags_string)

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
    if not article: abort(404)
    return render_template('history.html', article=article, revisions=revisions)

@app.route('/article/<int:article_id>/delete', methods=['POST'])
@login_required
@admin_required
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

@app.route('/api/preview', methods=['POST'])
@login_required
def api_preview():
    content = request.json.get('content', '')
    wiki_link_pattern = r'\[\[(.*?)\]\]'
    processed_content = re.sub(wiki_link_pattern, r'<span style="color:var(--primary-color); border-bottom:1px dashed var(--primary-color);">\1</span>', content)
    md = markdown2.Markdown(extras=['break-on-newline', 'cuddled-lists', 'tables', 'fenced-code-blocks'])
    html = md.convert(processed_content)
    return jsonify({"html": html})

@app.route('/api/upload_image', methods=['POST'])
@login_required
def api_upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO media (filename) VALUES (%s)", (filename,))
        conn.commit()
        cursor.close()
        conn.close()
    return jsonify({"url": url_for('static', filename='uploads/' + filename)})

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
                WHERE t.name = %s ORDER BY a.id DESC
            """, (tag_name,))
            articles = cursor.fetchall()
            for a in articles:
                a['snippet'] = generate_snippet(a['content_markdown'])
                a['thumbnail'] = extract_first_image(a['content_markdown'])
        except Exception as e:
            pass
        finally:
            cursor.close()
            conn.close()
    return render_template('tag_articles.html', articles=articles, tag_name=tag_name)

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
                WHERE a.title LIKE %s OR a.content_markdown LIKE %s OR t.name LIKE %s
                ORDER BY a.id DESC
            """, (search_term, search_term, search_term))
            articles = cursor.fetchall()
            for a in articles:
                a['snippet'] = generate_snippet(a['content_markdown'])
                a['thumbnail'] = extract_first_image(a['content_markdown'])
        except Exception as e:
            pass
        finally:
            cursor.close()
            conn.close()
    return render_template('search_results.html', articles=articles, query=query)

@app.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_categories():
    conn = get_db_connection()
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        parent_id = request.form.get('parent_id')
        parent_id = int(parent_id) if parent_id and parent_id.strip() else None
        
        if name and name.strip():
            clean_name = name.strip()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO categories (name, parent_id) VALUES (%s, %s)", (clean_name, parent_id))
                    conn.commit()
                    flash('Category added!', 'success')
                except Exception as e:
                    error = "Category already exists."
                finally:
                    cursor.close()
                    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c1.id, c1.name, c2.name as parent_name 
            FROM categories c1 
            LEFT JOIN categories c2 ON c1.parent_id = c2.id 
            ORDER BY c1.name ASC
        """)
        categories = cursor.fetchall()
        cursor.execute("SELECT id, name FROM categories WHERE parent_id IS NULL ORDER BY name ASC")
        parent_candidates = cursor.fetchall()
        cursor.close()
        conn.close()
    else:
        categories = []
        parent_candidates = []
        
    return render_template('manage_categories.html', categories=categories, parent_candidates=parent_candidates, error=error)

@app.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form.get('name')
        parent_id = request.form.get('parent_id')
        parent_id = int(parent_id) if parent_id and parent_id.strip() else None
        
        if name and conn:
            if parent_id == id:
                parent_id = None
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE categories SET name = %s, parent_id = %s WHERE id = %s", (name, parent_id, id))
                conn.commit()
            except Exception as e:
                pass
            finally:
                cursor.close()
        return redirect(url_for('manage_categories'))
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories WHERE id = %s", (id,))
        category = cursor.fetchone()
        cursor.execute("SELECT id, name FROM categories WHERE parent_id IS NULL AND id != %s ORDER BY name ASC", (id,))
        parent_candidates = cursor.fetchall()
        cursor.close()
        conn.close()
        if category:
            return render_template('edit_category.html', category=category, parent_candidates=parent_candidates)
    return redirect(url_for('manage_categories'))

@app.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM categories WHERE id = %s", (id,))
            conn.commit()
        except Exception as e:
            pass
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('manage_categories'))

@app.route('/media')
@login_required
@admin_required
def media_library():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM media ORDER BY id DESC")
        media_files = cursor.fetchall()
    except Exception as e:
        media_files = []
    finally:
        cursor.close()
        conn.close()
    return render_template('media.html', media_files=media_files)

@app.route('/media/<int:media_id>/delete', methods=['POST'])
@login_required
@admin_required
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
            flash('Error deleting media.', 'error')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('media_library'))

@app.route('/users')
@login_required
@admin_required
def manage_users():
    conn = get_db_connection()
    users = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, username, role FROM users ORDER BY id ASC")
            users = cursor.fetchall()
        except Exception as e:
            pass
        finally:
            cursor.close()
            conn.close()
    return render_template('manage_users.html', users=users)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    conn = get_db_connection()
    if request.method == 'POST':
        new_role = request.form.get('role')
        if new_role in ['Guest', 'Editor', 'Admin']:
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
                    conn.commit()
                    if session.get('user_id') == user_id:
                        session['role'] = new_role
                    flash('User role updated!', 'success')
                    return redirect(url_for('manage_users'))
                except Exception as e:
                    flash('Error updating user.', 'error')
                finally:
                    cursor.close()
                    conn.close()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user: abort(404)
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == session.get('user_id'):
        flash('You cannot delete yourself.', 'error')
        return redirect(url_for('manage_users'))
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            flash('User deleted.', 'info')
        except Exception as e:
            flash('Error deleting user.', 'error')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('manage_users'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if new_password:
            hashed_password = generate_password_hash(new_password)
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed_password, session['user_id']))
                    conn.commit()
                    flash('Password updated successfully.', 'success')
                except Exception as e:
                    flash('Error updating password.', 'error')
                finally:
                    cursor.close()
    stats = {'edits': 0}
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as cnt FROM revisions WHERE author_id = %s", (session['user_id'],))
        res = cursor.fetchone()
        if res:
            stats['edits'] = res['cnt']
        cursor.close()
        conn.close()
    return render_template('profile.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True)