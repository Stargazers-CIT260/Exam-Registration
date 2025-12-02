from flask import Flask
from flask import url_for
from flask import redirect
from flask import request
from flask import render_template
from flask import session
from markupsafe import escape
from flaskext.mysql import MySQL
from email_validator import validate_email, EmailNotValidError
from os import urandom

app = Flask(__name__)
app.secret_key = urandom(24)  # Generate a secure secret key for sessions

# MySQL Configuration
app.config['MYSQL_DATABASE_HOST'] = 'tramaway.proxy.rlwy.net'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'OnqbvfzavPfTNvrbNVQCYtgAqwhOvoMN'
app.config['MYSQL_DATABASE_DB'] = 'railway'
app.config['MYSQL_DATABASE_PORT'] = 56717


mysql = MySQL()
mysql.init_app(app)

def validate_login(username, password, role):
    cursor = mysql.get_db().cursor()
    try:
        cursor.execute('SELECT Password, Role FROM Users WHERE Email = %s LIMIT 1', (username,))
        (user_password, user_role) = cursor.fetchone()
    except:
        return False
    finally:
        cursor.close()
    return password == user_password and role == user_role

def normalize_email(email):
    # validate and get info
    email_info = validate_email(email, check_deliverability=False)
    # replace with normalized form
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
            # email is not valid, exception message is human-readable
            msg = str(e)
            return render_template('index.html', msg=msg)
        if request.path == '/faculty-login':
            if validate_login(username, password, 'faculty'):
                # session['loggedin'] = True
                # session['id'] = account['id']
                # session['username'] = account['username']
                return redirect('/faculty-dash')
            else:
                msg = 'Incorrect username/password!'
        else:
            if validate_login(username, password, 'student'):
                # session['loggedin'] = True
                # session['id'] = account['id']
                # session['username'] = account['username']
                return redirect('/student-dash')
            else:
                msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)

@app.route('/student-dash')
def student_dash():
    return render_template('student-dash.html')

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

# Student Dashboard - Check Exam Scheduling Status
@app.route('/student-dash/check-status', methods=['GET', 'POST'])
def check_status():
    exam_details = []
    msg = ''
    if request.method == 'POST':
        nshe_number = request.form['nshe-number']
        cursor = mysql.get_db().cursor()
        try:
            cursor.execute('SELECT * FROM Exams WHERE NSHE_Number = %s', (nshe_number,))
            exam_details = cursor.fetchall()
            # Logic to check exam scheduling status using nshe_number
            if exam_details:
                msg = "You have an exam scheduled."
            else:
                msg = "You do not have an exam scheduled."
        except Exception as e:
            print(e)
            msg = "An error occurred while fetching exam details."
            exam_details = []
        finally:
            cursor.close()
        return render_template('student-dash.html', msg=msg, exam_details=exam_details)
    
    # Maximum amount of exams a student can have.
    max_exams = 3
    if (len(exam_details) >=  max_exams):
        msg = "You have reached the maximum number of exams allowed."
        return render_template('student-dash.html', msg=msg, exam_details=exam_details)
    if (len(exam_details) == 0):
        msg = "You don't have any exams scheduled."
        return render_template('student-dash.html', msg=msg, exam_details=exam_details)
    if (len(exam_details) == 1):
        msg = "You can schedule 2 more exams."
        return render_template('student-dash.html', msg=msg, exam_details=exam_details)
    if (len(exam_details) == 2):
        msg = "You can schedule 1 more exam."
        return render_template("student-dash.html", msg=msg, exam_details=exam_details)

# Scheduling an exam
@app.route('/student-dash/schedule=exam', methods=['GET', 'POST'])
def schedule_exams():
    msg = ''
    if request.method == 'POST':
        nshe_number = request.form['nshe-number']
        course_code = request.form['course-code']
        exam_date = request.form['exam-date']
        cursor = mysql.get_db().cursor()
        try:
            cursor.execute('INSERT INTO Exams (NSHE_Number, Course_Code, Exam_Date) VALUES (%s, %s, %s)',)
            (nshe_number, course_code, exam_date)
            mysql.get_db().commit()
            msg = "Exam registered and scheduled successfully."
            your_exam = {
                'NSHE_Number': nshe_number,
                'Course_Code' : course_code,
                'Exam_date' : exam_date,
            }
            return render_template('student-dash.html', msg=msg, your_exam=your_exam)
        except Exception as e:
            print(e)
            msg= "An error occurred while scheduling the exam."
        finally:
            cursor.close()
            return render_template('student-dash.html', msg=msg)
        