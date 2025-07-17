
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

def get_db():
    conn = sqlite3.connect('data.db', check_same_thread=False)
    return conn

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        userid = request.form['userid']
        password = request.form['password']

        if role == 'admin' and userid == 'KSAcademySalem' and password == 'KS!Academy$123':
            session['user'] = 'admin'
            return redirect('/admin')
        elif role == 'student':
            with get_db() as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM students WHERE userid=? AND password=?", (userid, password))
                student = cur.fetchone()
            if student:
                session['user'] = student[2]
                session['name'] = student[1]
                return redirect('/student')
        return "Invalid login!"
    return render_template('login.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session.get('user') != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        userid = request.form['userid']
        password = request.form['password']
        category = request.form['category']
        try:
            with get_db() as con:
                cur = con.cursor()
                cur.execute("SELECT COUNT(*) FROM students WHERE userid = ?", (userid,))
                if cur.fetchone()[0] > 0:
                    return "User ID already exists!"
                con.execute("INSERT INTO students (name, userid, password, category) VALUES (?, ?, ?, ?)", 
                            (name, userid, password, category))
                con.commit()
        except Exception as e:
            return f"Error while adding student: {str(e)}"

    with get_db() as con:
        pgtrb = con.execute("SELECT * FROM students WHERE category = 'PG TRB'").fetchall()
        ugtrb = con.execute("SELECT * FROM students WHERE category = 'UG TRB'").fetchall()
        aptrb = con.execute("SELECT * FROM students WHERE category = 'AP TRB'").fetchall()
        tnset = con.execute("SELECT * FROM students WHERE category = 'TNSET'").fetchall()
        materials = con.execute("SELECT * FROM materials").fetchall()

    return render_template("admin.html",
        pgtrb=pgtrb,
        ugtrb=ugtrb,
        aptrb=aptrb,
        tnset=tnset,
        materials=materials)


@app.route('/delete_student', methods=['POST'])
def delete_student():
    if session.get('user') != 'admin':
        return redirect('/login')

    userid = request.form['userid']
    with get_db() as con:
        con.execute("DELETE FROM students WHERE userid = ?", (userid,))
        con.commit()
    return redirect('/admin')

@app.route('/add_material', methods=['POST'])
def add_material():
    if session.get('user') != 'admin':
        return redirect('/login')
    title = request.form['title']
    link = request.form['link']
    category = request.form['category']
    try:
        with get_db() as con:
            con.execute("INSERT INTO materials (title, link, category) VALUES (?, ?, ?)", (title, link, category))
            con.commit()
    except Exception as e:
        return f"Error while adding material: {str(e)}"
    return redirect('/admin')

@app.route('/delete_material', methods=['POST'])
def delete_material():
    if session.get('user') != 'admin':
        return redirect('/login')
    material_id = request.form['material_id']
    with get_db() as con:
        con.execute("DELETE FROM materials WHERE id = ?", (material_id,))
        con.commit()
    return redirect('/admin')

@app.route('/student')
def student():
    if not session.get('user') or session['user'] == 'admin':
        return redirect('/login')

    with get_db() as con:
        cur = con.cursor()
        cur.execute("SELECT name, category FROM students WHERE userid = ?", (session['user'],))
        student_data = cur.fetchone()

        if student_data:
            materials = con.execute("SELECT * FROM materials WHERE category = ?", (student_data[1],)).fetchall()
        else:
            materials = []

    return render_template("student.html",
                           student_name=student_data[0] if student_data else '',
                           userid=session.get('user'),
                           materials=materials)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/pgtrb')
def pgtrb():
    return render_template('pgtrb.html')


import pandas as pd
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_students', methods=['POST'])
def upload_students():
    if session.get('user') != 'admin':
        return redirect('/login')

    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Read file using pandas
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)

            required_cols = {'name', 'userid', 'password', 'category'}
            if not required_cols.issubset(set(df.columns)):
                return "Excel file must contain: name, userid, password, category"

            with get_db() as con:
                cur = con.cursor()
                added_count = 0
                for _, row in df.iterrows():
                    try:
                        cur.execute("INSERT INTO students (name, userid, password, category) VALUES (?, ?, ?, ?)",
                                    (row['name'], row['userid'], row['password'], row['category']))
                        added_count += 1
                    except sqlite3.IntegrityError:
                        continue  # skip duplicates
                con.commit()
            return f"{added_count} students added successfully."
        except Exception as e:
            return f"Error processing file: {str(e)}"
    else:
        return "Unsupported file format"

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
