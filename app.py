from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import json

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

        if role == 'admin' and userid == 'KSAcademySalem' and password == 'KS!Academy$4510$':
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
                    flash("User ID already exists!", "danger")
                    return redirect('/admin')
                con.execute("INSERT INTO students (name, userid, password, category) VALUES (?, ?, ?, ?)", 
                            (name, userid, password, category))
                con.commit()
                flash("Student added successfully!", "success")
        except Exception as e:
            flash(f"Error while adding student: {str(e)}", "danger")
            return redirect('/admin')

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
    flash("Student deleted successfully!", "success")
    return redirect('/admin')


# ============================================
# BULK DELETE STUDENTS - NEW ROUTE
# ============================================
@app.route('/bulk_delete_students', methods=['POST'])
def bulk_delete_students():
    if session.get('user') != 'admin':
        return redirect('/login')
    
    try:
        # Get the JSON string from form data
        userids_json = request.form.get('userids')
        
        if not userids_json:
            flash('No students selected', 'danger')
            return redirect('/admin')
        
        # Parse JSON array
        userids = json.loads(userids_json)
        
        if not userids:
            flash('No students selected', 'danger')
            return redirect('/admin')
        
        # Delete students
        with get_db() as con:
            deleted_count = 0
            for userid in userids:
                cur = con.execute("DELETE FROM students WHERE userid = ?", (userid,))
                deleted_count += cur.rowcount
            con.commit()
        
        flash(f'Successfully deleted {deleted_count} student(s)', 'success')
        
    except Exception as e:
        flash(f'Error deleting students: {str(e)}', 'danger')
    
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
        flash("Material added successfully!", "success")
    except Exception as e:
        flash(f"Error while adding material: {str(e)}", "danger")
    return redirect('/admin')

@app.route('/delete_material', methods=['POST'])
def delete_material():
    if session.get('user') != 'admin':
        return redirect('/login')
    material_id = request.form['material_id']
    with get_db() as con:
        con.execute("DELETE FROM materials WHERE id = ?", (material_id,))
        con.commit()
    flash("Material deleted successfully!", "success")
    return redirect('/admin')


# ============================================
# BULK DELETE MATERIALS - NEW ROUTE
# ============================================
@app.route('/bulk_delete_materials', methods=['POST'])
def bulk_delete_materials():
    if session.get('user') != 'admin':
        return redirect('/login')
    
    try:
        # Get the JSON string from form data
        material_ids_json = request.form.get('material_ids')
        
        if not material_ids_json:
            flash('No materials selected', 'danger')
            return redirect('/admin')
        
        # Parse JSON array
        material_ids = json.loads(material_ids_json)
        
        if not material_ids:
            flash('No materials selected', 'danger')
            return redirect('/admin')
        
        # Delete materials
        with get_db() as con:
            deleted_count = 0
            for material_id in material_ids:
                cur = con.execute("DELETE FROM materials WHERE id = ?", (material_id,))
                deleted_count += cur.rowcount
            con.commit()
        
        flash(f'Successfully deleted {deleted_count} material(s)', 'success')
        
    except Exception as e:
        flash(f'Error deleting materials: {str(e)}', 'danger')
    
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
        flash("No file part", "danger")
        return redirect('/admin')

    file = request.files['file']
    if file.filename == '':
        flash("No selected file", "danger")
        return redirect('/admin')

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
                flash("Excel file must contain: name, userid, password, category", "danger")
                return redirect('/admin')

            with get_db() as con:
                cur = con.cursor()
                added_count = 0
                skipped_count = 0
                for _, row in df.iterrows():
                    try:
                        cur.execute("INSERT INTO students (name, userid, password, category) VALUES (?, ?, ?, ?)",
                                    (row['name'], row['userid'], row['password'], row['category']))
                        added_count += 1
                    except sqlite3.IntegrityError:
                        skipped_count += 1
                        continue  # skip duplicates
                con.commit()
            
            message = f"{added_count} students added successfully."
            if skipped_count > 0:
                message += f" ({skipped_count} duplicates skipped)"
            flash(message, "success")
            
        except Exception as e:
            flash(f"Error processing file: {str(e)}", "danger")
            return redirect('/admin')
    else:
        flash("Unsupported file format", "danger")
    
    return redirect('/admin')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)