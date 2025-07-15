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
        try:
            with get_db() as con:
                # Check for duplicate userid
                cur = con.cursor()
                cur.execute("SELECT COUNT(*) FROM students WHERE userid = ?", (userid,))
                if cur.fetchone()[0] > 0:
                    return "User ID already exists!"
                con.execute("INSERT INTO students (name, userid, password) VALUES (?, ?, ?)", (name, userid, password))
                con.commit()
        except Exception as e:
            return f"Error while adding student: {str(e)}"

    with get_db() as con:
        students = con.execute("SELECT * FROM students").fetchall()
        materials = con.execute("SELECT * FROM materials").fetchall()

    return render_template("admin.html", students=students, materials=materials)

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
    try:
        with get_db() as con:
            con.execute("INSERT INTO materials (title, link) VALUES (?, ?)", (title, link))
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
        materials = con.execute("SELECT * FROM materials").fetchall()
        cur = con.cursor()
        cur.execute("SELECT name FROM students WHERE userid = ?", (session['user'],))
        student_data = cur.fetchone()

    return render_template("student.html",
                           student_name=student_data[0],
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

# Keep only this app.run block
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
