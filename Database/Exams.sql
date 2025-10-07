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

INSERT INTO exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_location)
VALUES ('C001', 'Math 101', '2025-12-20', '09:00:00', 90, 'North A101');
INSERT INTO exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_location)
VALUES ('C002', 'Science 101', '2025-12-18', '12:30:00', 90, 'South A103');
INSERT INTO exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_location)
VALUES ('C001', 'Math 102', '2025-12-18', '09:30:00', 90, 'South B101');
INSERT INTO exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_location)
VALUES ('C004', 'CIT 101', '2025-12-19', '10:00:00', 90, 'North C101');
INSERT INTO exams (course_id, exam_name, exam_date, exam_time, duration_min, exam_location)
VALUES ('C004', 'CIT 102', '2025-12-18', '11:00:00', 90, 'North A101');