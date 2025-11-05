-- =============================================
-- SQL Database File: Courses Table (THIS WILL BE THE ONLY SQL FILE THAT IS HEAVILY DOCUMENTED)
-- =============================================
-- Purpose: 
--   This file creates and populates the Courses table which stores
--   information about all available courses in the system.
--
-- Table Structure:
--   - Course_ID: Auto-generated unique identifier (e.g., C001)
--   - Course_name: The name of the course
--
-- Features:
--   - Automatic ID generation using a trigger
--   - Enforces unique course IDs
--   - Ensures course names are not empty
--
-- Usage:
--   Run this script to:
--   1. Create the Courses table structure
--   2. Set up the auto-numbering trigger
--   3. Insert initial course data
-- =============================================
-- CREATE TABLE: This statement creates a new table in the database
-- The syntax is: CREATE TABLE table_name (column_definitions)
CREATE TABLE Courses (
    -- Column definition format: column_name data_type [constraints]
    
    -- Course_ID: Unique identifier for each course
    -- VARCHAR(20): Can store text up to 20 characters
    -- PRIMARY KEY: Makes this column unique and not null, used to identify each row
    Course_ID VARCHAR(20) PRIMARY KEY,
    
    -- Course_name: Name of the course
    -- VARCHAR(100): Can store text up to 100 characters
    -- NOT NULL: This field cannot be empty
    Course_name VARCHAR(100) NOT NULL 
);

-- DELIMITER $$: Changes the delimiter from ; to $$ 
-- This is needed for creating triggers where we need multiple statements
DELIMITER $$

-- CREATE TRIGGER: Defines an automated action that runs when certain events occur
-- This trigger automatically generates a course ID when a new course is inserted
CREATE TRIGGER trg_course_id
BEFORE INSERT ON Courses    -- Runs before each INSERT operation on Courses table
FOR EACH ROW               -- Executes once for each row being inserted
BEGIN
    -- DECLARE: Creates a variable to store our next ID number
    DECLARE next_id INT;

    -- This SELECT statement calculates the next course ID number:
    -- 1. SUBSTRING(course_id, 2): Takes all characters after 'C' in the course_id
    -- 2. CAST(...AS UNSIGNED): Converts the string number to an integer
    -- 3. MAX(): Finds the highest current number
    -- 4. IFNULL(..., 0): If no courses exist yet, use 0
    -- 5. + 1: Add 1 to get the next number
    SELECT IFNULL(MAX(CAST(SUBSTRING(course_id, 2) AS UNSIGNED)), 0) + 1
    INTO next_id           -- Stores the result in our next_id variable
    FROM Courses;

    -- Creates the new course ID by:
    -- 1. CONCAT('C', ...): Adds 'C' at the start
    -- 2. LPAD(next_id, 3, '0'): Pads the number with zeros to make it 3 digits
    -- Example: C001, C002, etc.
    SET NEW.course_id = CONCAT('C', LPAD(next_id, 3, '0'));
END$$

DELIMITER ;  -- Changes the delimiter back to ;

-- INSERT INTO: Adds new rows to the table
-- Syntax: INSERT INTO table_name (column_list) VALUES (value_list)
-- Note: We don't need to specify Course_ID because our trigger handles that automatically

-- Initial set of courses
INSERT INTO Courses (Course_name) VALUES ('Math');        -- Will get ID C001
INSERT INTO Courses (Course_name) VALUES ('Science');     -- Will get ID C002
INSERT INTO Courses (Course_name) VALUES ('History');     -- Will get ID C003
INSERT INTO Courses (Course_name) VALUES ('Computer Science'); -- Will get ID C004
INSERT INTO Courses (Course_name) VALUES ('English');     -- Will get ID C005
INSERT INTO Courses (Course_name) VALUES ('Biology');     -- Will get ID C006

-- Additional courses
INSERT INTO Courses (Course_name) VALUES ('Art');         -- Will get ID C007
INSERT INTO Courses (Course_name) VALUES ('Psychology');  -- Will get ID C008
INSERT INTO Courses (Course_name) VALUES ('Accounting');  -- Will get ID C009
INSERT INTO Courses (Course_name) VALUES ('Economics');   -- Will get ID C010

