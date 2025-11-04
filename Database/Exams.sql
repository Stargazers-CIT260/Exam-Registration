CREATE TABLE Exams (
  Exam_ID       VARCHAR(12) PRIMARY KEY,   
  Course_ID     VARCHAR(10) NOT NULL,             
  Exam_Name     VARCHAR(100) NOT NULL UNIQUE,
  Exam_Date     DATE NOT NULL,
  Exam_Time     TIME NOT NULL,
  Duration_MIN INT NOT NULL,
  Exam_Location VARCHAR(100) NOT NULL,
  Capacity      INT  NOT NULL DEFAULT 20,
  FOREIGN KEY (Course_ID) REFERENCES Courses(Course_ID)
);


DELIMITER $$
CREATE TRIGGER trg_exam_id
BEFORE INSERT ON Exams
FOR EACH ROW
BEGIN
  DECLARE next_id INT;
  SELECT IFNULL(MAX(CAST(SUBSTRING(Exam_ID,3) AS UNSIGNED)),0) + 1
    INTO next_id
    FROM Exams;
  SET NEW.Exam_ID = CONCAT('EX', LPAD(next_id, 4, '0'));
END$$
DELIMITER ;


SET SQL_SAFE_UPDATES = 0;
DELETE FROM Exams;

INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C001', 'MATH 101', '2025-12-18', '09:00:00', 90, 'North', 'A103');
INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C001', 'MATH 102', '2025-12-18', '12:30:00', 90, 'South', 'C201');
INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C001', 'MATH 103', '2025-12-18', '15:00:00', 90, 'Henderson', 'A201');
INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C001', 'MATH 104', '2025-12-20', '09:00:00', 90, 'North', 'A103');
INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C001', 'MATH 105', '2025-12-20', '12:30:00', 90, 'South', 'C201');
INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C001', 'MATH 106', '2025-12-20', '15:30:00', 90, 'Henderson', 'A201');


INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C002', 'CHEM 101', '2025-12-18', '10:00:00', 90, 'North', 'A105');
INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C002', 'CHEM 102', '2025-12-18', '13:30:00', 90, 'South', 'B105');
INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C002', 'CHEM 103', '2025-12-18', '15:30:00', 90, 'Henderson', 'C101');
INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C002', 'CHEM 104', '2025-12-20', '13:00:00', 90, 'North', 'A105');
INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C002', 'CHEM 105', '2025-12-20', '13:30:00', 90, 'South', 'B105');
INSERT INTO Exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_campus, exam_building)
VALUES ('C002', 'CHEM 106', '2025-12-20', '15:30:00', 90, 'Henderson', 'C101');