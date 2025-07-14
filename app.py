from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

def get_db():
    conn = sqlite3.connect('data.db')
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
            con = get_db()
            cur = con.cursor()
            cur.execute("SELECT * FROM students WHERE userid=? AND password=?", (userid, password))
            student = cur.fetchone()
            con.close()
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
        con = get_db()
        con.execute("INSERT INTO students (name, userid, password) VALUES (?, ?, ?)", (name, userid, password))
        con.commit()
        con.close()

    con = get_db()
    students = con.execute("SELECT * FROM students").fetchall()
    materials = con.execute("SELECT * FROM materials").fetchall()
    con.close()
    return render_template("admin.html", students=students, materials=materials)

@app.route('/delete_student', methods=['POST'])
def delete_student():
    if session.get('user') != 'admin':
        return redirect('/login')

    userid = request.form['userid']
    con = get_db()
    con.execute("DELETE FROM students WHERE userid = ?", (userid,))
    con.commit()
    con.close()
    return redirect('/admin')

@app.route('/add_material', methods=['POST'])
def add_material():
    if session.get('user') != 'admin':
        return redirect('/login')
    title = request.form['title']
    link = request.form['link']
    con = get_db()
    con.execute("INSERT INTO materials (title, link) VALUES (?, ?)", (title, link))
    con.commit()
    con.close()
    return redirect('/admin')

@app.route('/delete_material', methods=['POST'])
def delete_material():
    if session.get('user') != 'admin':
        return redirect('/login')
    material_id = request.form['material_id']
    con = get_db()
    con.execute("DELETE FROM materials WHERE id = ?", (material_id,))
    con.commit()
    con.close()
    return redirect('/admin')

@app.route('/student')
def student():
    if not session.get('user') or session['user'] == 'admin':
        return redirect('/login')
    
    con = get_db()
    materials = con.execute("SELECT * FROM materials").fetchall()
    cur = con.cursor()
    cur.execute("SELECT name FROM students WHERE userid = ?", (session['user'],))
    student_data = cur.fetchone()
    con.close()

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

if __name__ == "__main__":
    app.run(debug=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

