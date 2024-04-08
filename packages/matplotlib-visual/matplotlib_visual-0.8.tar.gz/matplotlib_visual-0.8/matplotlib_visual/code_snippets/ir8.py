from flask import Flask, render_template, request
import sqlite3
app = Flask(_name_)
def create_index_db():
    conn = sqlite3.connect('search_index.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, title TEXT, content TEXT)''')
    conn.commit()
    conn.close()
def search(query):
    conn = sqlite3.connect('search_index.db')
    c = conn.cursor()
    c.execute("SELECT * FROM documents WHERE content LIKE ? OR title LIKE ?", ('%' + query + '%', '%' + query + '%'))
    results = c.fetchall()
    conn.close()
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def do_search():
    query = request.form.get('query')
    results = search(query)
    return render_template('results.html', results=results)

if _name_ == '_main_':
    create_index_db()
    app.run(debug=True)