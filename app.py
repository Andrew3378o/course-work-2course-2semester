import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-fallback-secret-key')

@app.route('/')
def index():
    return "Welcome to the Thematic Wiki!"

if __name__ == '__main__':
    app.run(debug=True)