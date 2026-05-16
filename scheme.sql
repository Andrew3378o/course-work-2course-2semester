CREATE DATABASE IF NOT EXISTS thematic_wiki CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE thematic_wiki;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Guest', 'Editor', 'Admin') DEFAULT 'Guest',
    status ENUM('Active', 'Blocked') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INT DEFAULT NULL,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    content_markdown TEXT NOT NULL,
    category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE revisions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT NOT NULL,
    author_id INT NOT NULL,
    old_content TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE article_tags (
    article_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (article_id, tag_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE media (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    article_id INT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE SET NULL
);

INSERT INTO categories (id, name, parent_id) VALUES
(1, 'Science & Nature', NULL),
(2, 'Technology & Computing', NULL),
(3, 'Arts & Culture', NULL),
(4, 'History & Events', NULL),

(5, 'Physics', 1),
(6, 'Biology', 1),
(7, 'Chemistry', 1),
(8, 'Astronomy & Space', 1),
(9, 'Earth Sciences', 1),
(10, 'Mathematics', 1),

(11, 'Programming', 2),
(12, 'Artificial Intelligence', 2),
(13, 'Cybersecurity', 2),
(14, 'Hardware & Architecture', 2),
(15, 'Web Development', 2),
(16, 'Data Science', 2),

(17, 'Literature', 3),
(18, 'Cinema & Television', 3),
(19, 'Music', 3),
(20, 'Visual Arts', 3),
(21, 'Philosophy', 3),

(22, 'Ancient History', 4),
(23, 'Medieval History', 4),
(24, 'Modern History', 4),
(25, 'Military History', 4),
(26, 'Contemporary Events', 4);