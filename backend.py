from flask import Flask
from flask import url_for
from flask import redirect
from flask import request
from flask import render_template
from markupsafe import escape
from flaskext.mysql import MySQL
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'Exam_Registration'
app.config['MYSQL_DATABASE_PASSWORD'] = 'admin'
app.config['MYSQL_DATABASE_DB'] = 'Exam_Registration'

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
        cursor = mysql.get_db().cursor()
        try:
            cursor.execute('INSERT INTO Users (Email, First_Name, Last_name, Password, Role) VALUES (%s, %s, %s, %s, %s)', (email, first_name, last_name, password, role))
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
