from datetime import datetime
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

# Command to run: flask --debug --app backend run
app = Flask(__name__)

app.secret_key = "supersecretkey"
# MySQL Configuration
app.config["MYSQL_DATABASE_HOST"] = "tramway.proxy.rlwy.net"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = "OnqbvfzavPfTNvrbNVQCYtgAqwhOvoMN"
app.config["MYSQL_DATABASE_DB"] = "railway"
app.config["MYSQL_DATABASE_PORT"] = 56717

mysql = MySQL()
mysql.init_app(app)


def validate_login(username, password, role):
    cursor = mysql.get_db().cursor()
    try:
        cursor.execute(
            "SELECT Password, Role FROM Users WHERE Email = %s LIMIT 1", (username,)
        )  # update from this below
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


@app.route("/")
@app.route("/student-login", methods=["GET", "POST"])
@app.route("/faculty-login", methods=["GET", "POST"])
def login():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        try:
            username = normalize_email(username)
        except EmailNotValidError as e:
            msg = str(e)
            return render_template("index.html", msg=msg)
        if request.path == "/faculty-login":
            if validate_login(username, password, "faculty"):
                session["user_email"] = username
                session["user_role"] = "faculty"
                return redirect("/faculty-dash")
            else:
                msg = "Incorrect username/password!"
        else:
            if validate_login(username, password, "student"):
                session["user_email"] = username
                session["user_role"] = "student"
                return redirect("/student-dash")
            else:
                msg = "Incorrect username/password!"
    return render_template("index.html", msg=msg)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- Registration page route ---
@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if request.method == "POST":
        first_name = request.form["first-name"].lower()
        last_name = request.form["last-name"].lower()
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm-password"]
        role = ""
        if (
            first_name == ""
            or last_name == ""
            or email == ""
            or password == ""
            or confirm_password == ""
        ):
            msg = "Please fill all fields"
            return render_template("registration.html", msg=msg)
        if password != confirm_password:
            msg = "Passwords do not match"
            return render_template("registration.html", msg=msg)

        try:
            email = normalize_email(email)
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            msg = str(e)
            return render_template("registration.html", msg=msg)
        if email.endswith("@student.csn.edu"):
            role = "student"
        elif email.endswith("@csn.edu"):
            role = "faculty"
        else:
            msg = "Please enter a valid CSN email address"
            return render_template("registration.html", msg=msg)

        if role == "student" and not email[:10].isnumeric():
            msg = "Student must use NSHE number in email"
            return render_template("registration.html", msg=msg)

        if role == "student" and password != email[:10]:
            msg = "Student password must be NSHE number"
            return render_template("registration.html", msg=msg)

        cursor = mysql.get_db().cursor()
        try:
            cursor.execute(
                "INSERT INTO Users (Email, First_Name, Last_name, Password, Role) VALUES (%s, %s, %s, %s, %s)",
                (email, first_name, last_name, password, role),
            )
            mysql.get_db().commit()
        except:
            msg = "Account already registered with that email address"
            return render_template("registration.html", msg=msg)
        finally:
            cursor.close()
        
        # Success with registration
        flash('Successfully Registered! Please Log In')
        return redirect(url_for('login'))

    return render_template("registration.html")


# --- faculty dashboard route ---
@app.route("/faculty-dash")
def faculty_dash():
    if "user_email" not in session:
        return redirect(url_for("login"))

    db = mysql.get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT First_Name, Last_Name, Role FROM Users WHERE Email = %s",
            (session["user_email"],),
        )
        row = cursor.fetchone()
    finally:
        cursor.close()

    faculty_name = "FACULTY"
    user_role = None
    if row:
        first_name, last_name, user_role = row
        faculty_name = f"{first_name} {last_name}".upper()

    # Deny access if signed-in user is not faculty
    if user_role != "faculty":
        # If they are a logged-in student, redirect to student dashboard; otherwise send to login
        if user_role == "student":
            return redirect(url_for("student_dash"))
        return redirect(url_for("login"))

    # Provide list of exams THIS faculty proctors
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT DISTINCT Exam_Name
            FROM Exams
            WHERE Proctor_Email = %s
            ORDER BY Exam_Name
            """,
            (session["user_email"],), 
        )
        exam_names = [r[0] for r in cursor.fetchall()]
    finally:
        cursor.close()

    # Fetch all exams from the database with sorting (so that they can be displayed on faculty page)
    sort_by = request.args.get("sort", "date")  # default sort by date
    selected_exam = request.args.get("exam", None)

    cursor = db.cursor()
    try:
        base_query = """
            SELECT
            e.Exam_ID,
            e.Exam_Name,
            e.Exam_Date,
            e.Exam_Time, 
            e.Exam_Campus,
            e.Exam_Location,
            e.Duration_MIN,
            (
                SELECT COUNT(*)
                FROM Registrations r
                WHERE r.Exam_ID = e.Exam_ID
                    AND r.status = 'active'
            ) AS Capacity
            FROM Exams e
            WHERE e.Proctor_Email = %s
        """
        params = [session["user_email"]]

        # if filter by exam name
        if sort_by == "name" and selected_exam:
            base_query += " AND Exam_Name = %s"
            params.append(selected_exam)
        
        # apply ORDER BY based on sort_by
        if sort_by == "location":
            order_by = " ORDER BY Exam_Campus, Exam_Location, Exam_Date, Exam_Time"
        elif sort_by == "name":
            # if no specific exam selected, still sort by name
            order_by = " ORDER BY Exam_Name, Exam_Date, Exam_Time"
        else:  # default: date/time
            order_by = " ORDER BY Exam_Date, Exam_Time"

        final_query = base_query + order_by

        cursor.execute(final_query, tuple(params))
        exams = _rows_to_dicts(cursor, cursor.fetchall())
    finally:
        cursor.close()
    
    # NEW: Fetch all registrations with student names
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            SELECT r.Exam_ID, u.First_Name, u.Last_Name
            FROM Registrations r
            JOIN Users u ON r.Student_Email = u.Email
            WHERE r.status = 'active'
        """
        )
        registrations = cursor.fetchall()
    finally:
        cursor.close()

    # Build mapping exam_id → list of student names
    exam_students = {}
    for exam_id, first, last in registrations:
        exam_students.setdefault(exam_id, []).append(f"{first} {last}")

    # Attach student list to each exam dictionary
    for exam in exams:
        exam_id = exam["Exam_ID"]
        exam["students"] = exam_students.get(exam_id, [])

    return render_template(
        "faculty-dash.html",
        faculty_name=faculty_name,
        exams=exams,
        sort_by=sort_by,
        exam_names=exam_names,
        selected_exam=selected_exam,
    )


# --- student dashboard route ---
@app.route('/student-dash')
def student_dash():
    if 'user_email' not in session or 'user_role' not in session:
        return redirect(url_for('login'))

    if session['user_role'] != 'student':
        if session['user_role'] == 'faculty':
            return redirect(url_for('faculty_dash'))
        return redirect(url_for('login'))

    student_email = session['user_email']
    db = mysql.get_db()
    cursor = db.cursor()

    try:
        # Fetch student info (name, email, student ID)
        cursor.execute("""
            SELECT First_Name, Last_Name
            FROM Users
            WHERE Email = %s
        """, (student_email,))
        row = cursor.fetchone()

        student_name = "STUDENT"
        student_id = ""
        if row:
            first_name, last_name = row
            student_name = f"{first_name} {last_name}".upper()
            student_id = student_email.split("@")[0]


        # Fetch upcoming exams
        cursor.execute("""
            SELECT e.Exam_ID, e.Exam_Name, e.Exam_Date, e.Exam_Time, e.Exam_Campus, e.Exam_Location
            FROM Registrations r
            JOIN Exams e ON r.Exam_ID = e.Exam_ID
            WHERE r.Student_Email = %s
              AND r.status = 'active'
              AND e.Exam_Date >= CURDATE()
            ORDER BY e.Exam_Date, e.Exam_Time
        """, (student_email,))
        exams_raw = cursor.fetchall()
        exams = []
        for exam in exams_raw:
            exam_id, name, date, time, campus, location = exam

            if isinstance(date, datetime):
                date_str = date.strftime("%m/%d/%Y")
            else:
                date_str = datetime.strptime(str(date), "%Y-%m-%d").strftime("%m/%d/%Y")

            if isinstance(time, datetime):
                time_str = time.strftime("%I:%M %p")
            else:
                time_str = datetime.strptime(str(time), "%H:%M:%S").strftime("%I:%M %p")

            exams.append((exam_id, name, date_str, time_str, campus, location))




    finally:
        cursor.close()

    if not exams:
        message = "NO UPCOMING EXAMS SCHEDULED"
        return render_template('student-dash.html',
                               student_name=student_name,
                               student_email=student_email,
                               student_id=student_id,
                               exams=None,
                               message=message)

    return render_template('student-dash.html',
                           student_name=student_name,
                           student_email=student_email,
                           student_id=student_id,
                           exams=exams,
                           message=None)


# --- cancel exam route ---
@app.route('/cancel-exam/<exam_id>', methods=['POST'])
def cancel_exam(exam_id):
    if 'user_email' not in session or session.get('user_role') != 'student':
        return redirect(url_for('login'))

    student_email = session['user_email']
    db = mysql.get_db()
    cur = db.cursor()

    try:
        # --- make sure registraion exist and active ---
        cur.execute("""
            SELECT 1
            FROM Registrations
            WHERE Student_Email = %s AND Exam_ID = %s AND status = 'active'
            LIMIT 1
            """, (student_email, exam_id))
        
        if not cur.fetchone():
            flash("You are not registered for this exam.")
            return redirect(url_for("student_dash"))
        
        # --- hard DELETE active registration row ---
        cur.execute("""
            DELETE FROM Registrations
            WHERE Student_Email = %s 
                AND Exam_ID = %s 
                AND status = 'active'
        """, (student_email, exam_id))

        db.commit()
        flash("Your exam reservation has been canceled.")

    except Exception as e:
        db.rollback()
        print("Cancel Error:", e)
        flash("Error canceling exam. Please try again.")
    finally:
        cur.close()

    return redirect(url_for('student_dash'))

# convert SQL rows to dicts
def _rows_to_dicts(cursor, rows):
    cols = [d[0] for d in cursor.description]
    return [{cols[i]: r[i] for i in range(len(cols))} for r in rows]


# Route for scheduling page
@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    if "user_email" not in session:  # require login
        return redirect(url_for("login"))

    db = mysql.get_db()

    # ---- POST: handle registration/ scheduling ----
    if request.method == "POST":
        exam_id = request.form.get("exam_id")
        if not exam_id:
            flash("Please select an exam.")
            return redirect(url_for("schedule"))

        student_email = session["user_email"]

        cur = db.cursor()
        try:
            # --- get exam name ---
            cur.execute ("""
                SELECT Exam_Name
                FROM Exams
                WHERE Exam_ID = %s
            """, (exam_id,))
            row = cur.fetchone()
            if not row:
                flash("Selected exam not found. Please try again.")
                return redirect(url_for("schedule"))
            
            exam_name = row[0]
            
            # --- check duplicate for SAME EXAM ---
            cur.execute(
                """
                SELECT 1
                FROM Registrations r
                JOIN Exams e ON r.Exam_ID = e.Exam_ID
                WHERE r.Student_Email = %s 
                    AND r.status = 'active'
                    AND e.Exam_Name = %s
                LIMIT 1
            """,
                (student_email, exam_name))
            
            if cur.fetchone():
                flash("You are already registered for same exam. "
                      "Please cancel your existing exam before scheduling another.")
                return redirect(url_for('schedule'))
            
            # ---- Max 3 classes ----
            cur.execute("""
                SELECT COUNT(*)
                FROM Registrations
                WHERE Student_Email = %s
                    AND status = 'active'
            """, (student_email,)
            )
            active_count = cur.fetchone()[0]
            
            if active_count >= 3:
                flash("You can only register for up to 3 exams. "
                      "Please cancel before scheduling another.")
                return redirect(url_for('schedule'))
            
            # --- check capacity based on active registration ---
            cur.execute("""
                SELECT COUNT(*)
                FROM Registrations
                WHERE Exam_ID = %s
                    AND status = 'active'
            """, (exam_id,))

            seats_taken = cur.fetchone()[0]
            if seats_taken >=20:
                flash("Sorry, this exam is full.")
                return redirect(url_for("schedule"))
            
            # --- Insert scheduled exam into registration row ---
            cur.execute(
                """
                INSERT INTO Registrations (Student_Email, Exam_ID, status)
                VALUES (%s, %s, 'active')
            """, (student_email, exam_id)
            )

            db.commit()

            # --- to to confirmation page ---
            return redirect(url_for('exam_confirm', exam_id=exam_id))

        except Exception as e:
            db.rollback()
            print("Error while Scheduling:", repr(e))
            flash("Unexpected error while scheduling. Please try again.")
        
        finally:
            cur.close()

    # ----- GET: show table of available exams -----
    cursor = db.cursor()
    try:
        # --- filter query string ---
        exam_name_filter = request.args.get("exam_name", "").strip()
        date_filter = request.args.get("exam_date", "").strip()
        campus_filter = request.args.get("campus", "").strip()

        # --- dynamic WHERE clause ---
        where_clauses = [
            "e.Exam_Date >= CURDATE()",
            """(
                SELECT COUNT(*)
                FROM Registrations r
                WHERE r.Exam_ID = e.Exam_ID
                    AND r.status = 'active'
                ) < 20 """
        ]
        params = []

        if exam_name_filter:
            where_clauses.append("e.Exam_Name = %s")
            params.append(exam_name_filter)

        if date_filter:
            where_clauses.append("e.Exam_Date = %s")
            params.append(date_filter)
        
        if campus_filter:
            where_clauses.append("e.Exam_Campus = %s")
            params.append(campus_filter)
        
        where_sql = " AND ".join(where_clauses)

        query = f"""
            SELECT
                e.Exam_ID,
                e.Course_ID,
                e.Exam_Name,
                e.Exam_Date,
                e.Exam_Time,
                e.Duration_MIN,
                e.Exam_Campus,
                e.Exam_Location,
                (
                    SELECT COUNT(*)
                    FROM Registrations r
                    WHERE r.Exam_ID = e.Exam_ID
                      AND r.status = 'active'
                ) AS Capacity,        -- "seats taken" shown in last column
                e.Proctor_Email,
                CONCAT(u.First_Name, ' ', u.Last_Name) AS Proctor_Name
            FROM Exams e
            JOIN Users u
                ON e.Proctor_Email = u.Email
            WHERE {where_sql}
            ORDER BY e.Exam_Date, e.Exam_Time, e.Exam_Campus, e.Exam_Location, e.Exam_ID
        """
        
        cursor.execute(query, tuple(params))
        exams = _rows_to_dicts(cursor, cursor.fetchall())

        # --- dropdown options ---
        cursor.execute("SELECT DISTINCT Exam_Name FROM Exams ORDER BY Exam_Name")
        exam_name_options = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT Exam_Date FROM Exams ORDER BY Exam_Date")
        date_options = [str(row[0]) for row in cursor.fetchall()]  # cast date to string

        cursor.execute("SELECT DISTINCT Exam_Campus FROM Exams ORDER BY Exam_Campus")
        campus_options = [row[0] for row in cursor.fetchall()]

    finally:
        cursor.close()

    return render_template(
            "schedule.html", 
            exams=exams,
            exam_name_filter=exam_name_filter,
            date_filter=date_filter,
            campus_filter=campus_filter,
            exam_name_options=exam_name_options,
            date_options=date_options,
            campus_options=campus_options,)

# Route for exam confirmation page
@app.route('/schedule/confirm/<exam_id>')
def exam_confirm(exam_id):
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    db = mysql.get_db()
    cur = db.cursor()

    try:
        cur.execute("""
            SELECT Exam_ID, Exam_Name, Exam_Date, Exam_Time,
                    Exam_Campus, Exam_Location
            FROM Exams
            WHERE Exam_ID = %s
        """, (exam_id,)
        )
        row = cur.fetchone()
    finally:
        cur.close()
    
    exam = None
    if row:
        exam = {
            "id": row[0],
            "name": row[1],
            "date": str(row[2]),
            "time": str(row[3]),
            "campus": row[4],
            "location": row[5],
        }
    return render_template('exam-conf.html', exam=exam)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
