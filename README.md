# Thematic Wiki

A web-based thematic wiki application built with Flask and MySQL.

## Local Setup Instructions

### 1. Clone the repository
`git clone <your-repository-url>`
`cd <repository-folder-name>`

### 2. Set up the virtual environment
**Windows:**
`python -m venv venv`
`venv\Scripts\activate`

**Mac/Linux:**
`python3 -m venv venv`
`source venv/bin/activate`

### 3. Install dependencies
`pip install -r requirements.txt`

### 4. Database setup
1. Ensure MySQL Server is running.
2. Execute the `schema.sql` file in your MySQL client.

### 5. Environment variables
1. Copy `.env.example` to `.env`.
2. Update database credentials in `.env`.

### 6. Run the application
`python app.py`