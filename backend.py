from flask import Flask
from flask import url_for
from flask import redirect
from flask import request
from flask import render_template
from flask import session
from markupsafe import escape
from flaskext.mysql import MySQL
from email_validator import validate_email, EmailNotValidError


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

    #update validate login to avoid cashes
    #    (user_password, user_role) = cursor.fetchone()
    #except:
    #    return False
    #finally:
    #    cursor.close()
    #return password == user_password and role == user_role

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
                session['user_email'] = username
                # session['loggedin'] = True
                # session['id'] = account['id']
                # session['username'] = account['username']
                return redirect('/student-dash')
            else:
                msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)

@app.route('/student-dash')
def student_dash():
    if 'user_email' not in session:  #make sure the user is logged in and in session
        return redirect (url_for('login'))
    
    #get student's first and last name from DB
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
        student_name = f"{first_name} {last_name}".upper() #capitalized

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


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)