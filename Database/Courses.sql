CREATE TABLE Courses (
  Course_ID VARCHAR(20) PRIMARY KEY,
  Course_name VARCHAR(100) NOT NULL 
);

DELIMITER $$

CREATE TRIGGER trg_course_id
BEFORE INSERT ON Courses
FOR EACH ROW
BEGIN
  DECLARE next_id INT;

  SELECT IFNULL(MAX(CAST(SUBSTRING(course_id, 2) AS UNSIGNED)), 0) + 1
  INTO next_id
  FROM Courses;

  SET NEW.course_id = CONCAT('C', LPAD(next_id, 3, '0'));
END$$

DELIMITER ;


INSERT INTO Courses (Course_name) VALUES ('Computer And Information Technology');
INSERT INTO Courses (Course_name) VALUES ('Computer Science');
INSERT INTO Courses (Course_name) VALUES ('CISCO');
INSERT INTO Courses (Course_name) VALUES ('Graphic Information Systems');



