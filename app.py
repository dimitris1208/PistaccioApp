from flask import Flask, render_template, request, redirect, url_for, session
import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

client = MongoClient(os.environ.get('SECRET_URI'))
db = client['social_platform']
users_collection = db['users']
messages_collection = db['messages']

"""

def add_users():
    users = [
        {'username': 'friend1', 'password': generate_password_hash('code1')},
        {'username': 'friend2', 'password': generate_password_hash('code2')}
    ]
    users_collection.insert_many(users)

"""

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.users.find_one({"username": username, "password": password})
        if user:
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    messages = messages_collection.find().sort('timestamp', 1)
    return render_template('chat.html', username=session['username'], messages=messages)

@app.route('/post', methods=['POST'])
def post():
    if 'username' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    username = session['username']
    timestamp = datetime.utcnow()
    messages_collection.insert_one({'username': username, 'content': content, 'timestamp': timestamp})
    return redirect(url_for('chat'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

"""

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password == confirm_password:
            hashed_password = generate_password_hash(new_password)
            users_collection.update_one({'username': session['username']}, {'$set': {'password': hashed_password}})
            return redirect(url_for('chat'))
        else:
            return 'Passwords do not match'
    return render_template('change_password.html')

    
"""

def delete_old_messages():
    cutoff = datetime.utcnow() - timedelta(hours=12)
    messages_collection.delete_many({'timestamp': {'$lt': cutoff}})

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_old_messages, 'interval', hours=1)
    scheduler.start()

if __name__ == '__main__':
    start_scheduler()
    app.run(debug=True)
