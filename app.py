from flask import Flask, render_template, g, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'artfind.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/photos/<path:filename>')
def photos(filename):
    return send_from_directory(os.path.join(app.root_path, 'photos'), filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/artist')
def artist():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM artist')
    rows = cursor.fetchall()
    return render_template('artist.html', rows=rows)

@app.route('/main')
def main():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT name, style, tgid, username FROM artist')
    rows = cursor.fetchall()

    # Prepare a dictionary to hold photo paths for each artist
    artist_photos = {}
    for row in rows:
        tgid = row[2]
        directory = os.path.join(app.root_path, 'photos', str(tgid))
        if os.path.exists(directory):
            photos = os.listdir(directory)
            artist_photos[tgid] = photos
        else:
            artist_photos[tgid] = []

    return render_template('main.html', rows=rows, artist_photos=artist_photos)


@app.route('/customer')
def customer():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM customer')
    rows = cursor.fetchall()
    return render_template('customer.html', rows=rows)

@app.route('/delete_artist/<int:id>')
def delete_artist(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM artist WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('artist'))

@app.route('/delete_customer/<int:id>')
def delete_customer(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM customer WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('customer'))

if __name__ == '__main__':
    app.run(debug=True)