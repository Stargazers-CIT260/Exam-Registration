from flask import Flask
from flask import url_for
from flask import redirect
from flask import request
from flask import render_template
from flask import session
from flask import flash
from markupsafe import escape
from flaskext.mysql import MySQL
from email_validator import validate_email, EmailNotValidError
from markupsafe import escape

app = Flask(__name__)

app.secret_key = 'supersecretkey'
# MySQL Configuration
app.config['MYSQL_DATABASE_HOST'] = 'tramway.proxy.rlwy.net'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'OnqbvfzavPfTNvrbNVQCYtgAqwhOvoMN'
app.config['MYSQL_DATABASE_DB'] = 'railway'
app.config['MYSQL_DATABASE_PORT'] = 56717

mysql = MySQL()
mysql.init_app(app)

def validate_login(username, password, role):
    cursor = mysql.get_db().cursor()
    try:
        cursor.execute('SELECT Password, Role FROM Users WHERE Email = %s LIMIT 1', (username,))#update from this below
        row = cursor.fetchone()
        if not row:
            return False
        user_password, user_role = row
        return password == user_password and role == user_role
    finally:
        cursor.close()


def normalize_email(email):
    email_info = validate_email(email, check_deliverability=False)
    return email_info.normalized

@app.route('/')
@app.route('/student-login', methods=['GET', 'POST'])
@app.route('/faculty-login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        try:
            username = normalize_email(username)
        except EmailNotValidError as e:
            msg = str(e)
            return render_template('index.html', msg=msg)
        if request.path == '/faculty-login':
            if validate_login(username, password, 'faculty'):
                return redirect('/faculty-dash')
            else:
                msg = 'Incorrect username/password!'
        else:
            if validate_login(username, password, 'student'):
                session['user_email'] = username
                return redirect('/student-dash')
            else:
                msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)


@app.route('/student-dash')
def student_dash():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.get_db().cursor()
    try: 
        cursor.execute(
            'SELECT First_Name, Last_Name FROM Users WHERE Email = %s',
            (session['user_email'],)
        )
        row = cursor.fetchone()
    finally:
        cursor.close()  
    
    student_name = "STUDENT"
    if row:
        first_name, last_name = row
        student_name = f"{first_name} {last_name}".upper()

    return render_template('student-dash.html', student_name=student_name)
    

@app.route('/faculty-dash')
def faculty_dash():
    return render_template('faculty-dash.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        role = ''
        if first_name == '' or last_name == '' or email == '' or password == '' or confirm_password == '':
            msg = 'Please fill all fields'
            return render_template('registration.html', msg=msg)
        if password != confirm_password:
            msg = 'Passwords do not match'
            return render_template('registration.html', msg=msg)

        try:
            email = normalize_email(email)
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            msg = str(e)
            return render_template('registration.html', msg=msg)
        if email.endswith('@student.csn.edu'):
            role = 'student'
        elif email.endswith('@csn.edu'):
            role = 'faculty'
        else:
            msg = 'Please enter a valid CSN email address'
            return render_template('registration.html', msg=msg)

        if role == 'student' and not email[:10].isnumeric():
            msg = 'Student must use NSHE number in email'
            return render_template('registration.html', msg=msg)

        if role == 'student' and password != email[:10]:
            msg = 'Student password must be NSHE number'
            return render_template('registration.html', msg=msg)

        cursor = mysql.get_db().cursor()
        try:
            cursor.execute(
                'INSERT INTO Users (Email, First_Name, Last_name, Password, Role) VALUES (%s, %s, %s, %s, %s)',
                (email, first_name, last_name, password, role))
            mysql.get_db().commit()
        except:
            msg = "Account already registered with that email address"
            return render_template('registration.html', msg=msg)
        finally:
            cursor.close()

        if role == 'student':
            return redirect('/student-dash')
        else:
            return redirect('/faculty-dash')

    return render_template('registration.html')

# convert SQL rows to dicts
def _rows_to_dicts(cursor, rows):
    cols = [d[0] for d in cursor.description]
    return [{cols[i]: r[i] for i in range(len(cols))} for r in rows]


# Route for scheduling page
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if 'user_email' not in session:  # require login 
        return redirect(url_for('login'))
    

    db = mysql.get_db()
    cursor = db.cursor()

    # POST: handle registration 
    if request.method == 'POST':
        exam_id = request.form.get('exam_id')
        if not exam_id:
            flash("Please select an exam.")
            return redirect(url_for('schedule'))

        db = mysql.get_db()
        cur = db.cursor()
        try:
        # Atomically reserve a seat only if not full and not past date
            cur.execute("""
                UPDATE Exams
                SET Capacity = Capacity + 1
                WHERE Exam_ID = %s
                AND Capacity < 20
                AND Exam_Date >= CURDATE()
            """, (exam_id,))
            db.commit()

            if cur.rowcount == 0:
                flash("Sorry, this exam is full or no longer available.")
            else:
                flash(f"Registered for exam {exam_id}!")
        finally:
            cur.close()

        return redirect(url_for('schedule'))

    # ----- GET: show table of available exams -----
    try:
        cursor.execute("""
            SELECT Exam_ID, Course_ID, Exam_Name, Exam_Date, Exam_Time,
                   Duration_MIN, Exam_Campus, Exam_Building, Capacity
            FROM Exams
            WHERE Exam_Date >= CURDATE()
              AND Capacity < 20              -- hide full exams (20)
            ORDER BY Exam_Date, Exam_Time, Exam_Campus, Exam_Building, Exam_ID
        """)
        exams = _rows_to_dicts(cursor, cursor.fetchall())
    finally:
        cursor.close()

    return render_template('schedule.html', exams=exams)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)