1. **Install Python (Version 3.14.0 or later)**<br>
   <https://www.python.org/downloads/>
2. **Install MySQL**<br>
   <https://dev.mysql.com/downloads/mysql/><br>
   Click "Typical".<br>
   Make sure "Run MySQL Configurator" is checked.<br>
3. **Configure MySQL**<br>
   Leave everything on the first page as default.<br>
   Enter any password you wish for your Root Password.<br>
   Add a user (User Name: `Exam_Registration`, Password: `admin`).<br>
   Click "Next".<br>
   Click "Execute".<br>
   Click "Next".<br>
4. **Open the MySQL Command Line Client**
5. **Create the database**
   ```
   CREATE DATABASE Exam_Registration;
   GRANT ALL PRIVILAGES ON Exam_Registration.* TO 'Exam_Registration'@'%' WITH GRANT OPTION;
   USE Exam_Registration;
   ```
6. **Initialize database tables**
   ```
   source /path/to/project/Database/Courses.sql;
   source /path/to/project/Database/Exams.sql;
   source /path/to/project/Database/Users.sql;
   source /path/to/project/Database/Registrations.sql;
   ```
7. **Open a new terminal and CD to Where You Want the Repo**

8. **Clone git repository**
   ```
   > git clone https://github.com/Stargazers-CIT260/Exam-Registration.git
   ```
9. **Create a new virtual environment**
   ```
   > python -m venv .venv
   ```
10. **Activate the environment**<br>
    Windows:
    ```
    > .venv\scripts\activate
    ```
    Linux & Mac OS:
    ```
    > source .venv/bin/activate
    ```
11. **Install project dependencies**
    ```
    > pip install -r requirements.txt
    ```
12. **Run the debug server**
    ```
    > flask --debug --app backend run
    ```
