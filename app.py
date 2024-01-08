from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import sqlite3
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATABASE'] = 'database.db'
app.config['SECRET_KEY'] = ''
app.config['INSTAGRAM_ACCESS_TOKEN'] = ''

# Creating uploads directory if not exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to connect to the database
def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# Initializing the database
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Route for entering the username
@app.route('/')
def index():
    return render_template('index.html')

# Route to display the user's Instagram posts
@app.route('/profile', methods=['POST'])
def profile():
    username = request.form['username']

    # Fetching user's Instagram posts using the Graph API
    api_url = f'https://graph.instagram.com/v12.0/{username}?fields=id,media_type,media_url,thumbnail_url,caption,permalink,timestamp&access_token={app.config["INSTAGRAM_ACCESS_TOKEN"]}'
    response = requests.get(api_url)

    try:
        data = response.json()
        posts = data.get('data', [])
    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        posts = []

    return render_template('profile.html', username=username, posts=posts)


# Route to handle image selections and save to the database
@app.route('/save_images', methods=['POST'])
def save_images():
    username = request.form['username']
    selected_images = request.form.getlist('selected_images')

    # Saving selected images to the database
    db = get_db()
    for image in selected_images:
        db.execute('INSERT INTO images (username, filename) VALUES (?, ?)', (username, image))
    db.commit()

    return redirect(url_for('index'))  # Redirecting to the initial page after saving images

if __name__ == '__main__':
    init_db()  # Initializing the database
    app.run(debug=True)
