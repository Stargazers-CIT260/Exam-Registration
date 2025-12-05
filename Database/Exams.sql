CREATE TABLE Exams (
  Exam_ID       VARCHAR(12) PRIMARY KEY,   
  Course_ID     VARCHAR(10) NOT NULL,             
  Exam_Name     VARCHAR(100) NOT NULL UNIQUE,
  Exam_Date     DATE NOT NULL,
  Exam_Time     TIME NOT NULL,
  Duration_MIN INT NOT NULL,
  Exam_Campus VARCHAR(20) NOT NULL,
  Exam_Building VARCHAR(10) NOT NULL,
  Capacity      INT  NOT NULL DEFAULT 0,
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

ALTER TABLE Exams ADD UNIQUE KEY uq_exam_slot (Exam_Date, Exam_Time, Exam_Campus, Exam_Building);


INSERT INTO Exams (Course_ID, Exam_Name, Exam_Date, Exam_Time, Exam_Campus, Exam_Building, Duration_MIN) VALUES
-- ========= C001 – CIT 129 (dates: 12/08 09:30, 12/11 14:00, 12/12 15:00) =========
('C001','CIT 129','2025-12-08','08:00:00','North','C101',90),
('C001','CIT 129','2025-12-08','08:00:00','West','C105',90),
('C001','CIT 129','2025-12-08','08:00:00','Henderson','C114',90),
('C001','CIT 129','2025-12-10','11:00:00','North','C101',90),
('C001','CIT 129','2025-12-10','11:00:00','West','C105',90),
('C001','CIT 129','2025-12-10','11:00:00','Henderson','C114',90),
('C001','CIT 129','2025-12-12','14:00:00','North','C101',90),
('C001','CIT 129','2025-12-12','14:00:00','West','C105',90),
('C001','CIT 129','2025-12-12','14:00:00','Henderson','C114',90);

-- ========= C001 – CIT 130 (dates: 12/08 09:30, 12/11 14:00, 12/12 15:00) =========
INSERT INTO Exams (Course_ID, Exam_Name, Exam_Date, Exam_Time, Exam_Campus, Exam_Building, Duration_MIN) VALUES
('C001','CIT 130','2025-12-08','09:30:00','North','C107',90),
('C001','CIT 130','2025-12-08','09:30:00','West','C109',90),
('C001','CIT 130','2025-12-08','09:30:00','Henderson','C111',90),
('C001','CIT 130','2025-12-11','14:00:00','North','C107',90),
('C001','CIT 130','2025-12-11','14:00:00','West','C109',90),
('C001','CIT 130','2025-12-11','14:00:00','Henderson','C111',90),
('C001','CIT 130','2025-12-12','15:00:00','North','C107',90),
('C001','CIT 130','2025-12-12','15:00:00','West','C109',90),
('C001','CIT 130','2025-12-12','15:00:00','Henderson','C111',90);

 -- ========= C001 – CIT 131 (dates: 12/09 14:00, 12/11 08:00, 12/12 09:30) =========
INSERT INTO Exams (Course_ID, Exam_Name, Exam_Date, Exam_Time, Exam_Campus, Exam_Building, Duration_MIN) VALUES
('C002','CIT 131','2025-12-09','14:00:00','North','C201',90),
('C002','CIT 131','2025-12-09','14:00:00','West','C211',90),
('C002','CIT 131','2025-12-09','14:00:00','Henderson','C207',90),
('C002','CIT 131','2025-12-11','08:00:00','North','C201',90),
('C002','CIT 131','2025-12-11','08:00:00','West','C211',90),
('C002','CIT 131','2025-12-11','08:00:00','Henderson','C207',90),
('C002','CIT 131','2025-12-12','09:30:00','North','C201',90),
('C002','CIT 131','2025-12-12','09:30:00','West','C211',90),
('C002','CIT 131','2025-12-12','09:30:00','Henderson','C207',90);

-- ========= C002 – CS 135 (dates: 12/09 12:30, 12/10 14:00, 12/12 08:00) =========
INSERT INTO Exams (Course_ID, Exam_Name, Exam_Date, Exam_Time, Exam_Campus, Exam_Building, Duration_MIN) VALUES
('C001','CS 135','2025-12-09','12:30:00','North','C118',90),
('C001','CS 135','2025-12-09','12:30:00','West','C117',90),
('C001','CS 135','2025-12-09','12:30:00','Henderson','C205',90),
('C001','CS 135','2025-12-10','14:00:00','North','C118',90),
('C001','CS 135','2025-12-10','14:00:00','West','C117',90),
('C001','CS 135','2025-12-10','14:00:00','Henderson','C205',90),
('C001','CS 135','2025-12-12','08:00:00','North','C118',90),
('C001','CS 135','2025-12-12','08:00:00','West','C117',90),
('C001','CS 135','2025-12-12','08:00:00','Henderson','C205',90);


-- ========= C003 – CSCO 120 (dates: 12/08 14:00, 12/10 08:00, 12/11 09:30) =========
INSERT INTO Exams (Course_ID, Exam_Name, Exam_Date, Exam_Time, Exam_Campus, Exam_Building, Duration_MIN) VALUES
('C003','CSCO 120','2025-12-08','14:00:00','North','C101',90),
('C003','CSCO 120','2025-12-08','14:00:00','West','C105',90),
('C003','CSCO 120','2025-12-08','14:00:00','Henderson','C114',90),
('C003','CSCO 120','2025-12-10','08:00:00','North','C101',90),
('C003','CSCO 120','2025-12-10','08:00:00','West','C105',90),
('C003','CSCO 120','2025-12-10','08:00:00','Henderson','C114',90),
('C003','CSCO 120','2025-12-11','09:30:00','North','C101',90),
('C003','CSCO 120','2025-12-11','09:30:00','West','C105',90),
('C003','CSCO 120','2025-12-11','09:30:00','Henderson','C114',90);

-- ========= C004 – GRC 101 (dates: 12/08 15:00, 12/09 08:00, 12/10 09:30) =========
INSERT INTO Exams (Course_ID, Exam_Name, Exam_Date, Exam_Time, Exam_Campus, Exam_Building, Duration_MIN) VALUES
('C004','GRC 101','2025-12-08','15:00:00','North','C107',90),
('C004','GRC 101','2025-12-08','15:00:00','West','C109',90),
('C004','GRC 101','2025-12-08','15:00:00','Henderson','C111',90),
('C004','GRC 101','2025-12-09','08:00:00','North','C107',90),
('C004','GRC 101','2025-12-09','08:00:00','West','C109',90),
('C004','GRC 101','2025-12-09','08:00:00','Henderson','C111',90),
('C004','GRC 101','2025-12-10','09:30:00','North','C107',90),
('C004','GRC 101','2025-12-10','09:30:00','West','C109',90),
('C004','GRC 101','2025-12-10','09:30:00','Henderson','C111',90);


ALTER TABLE Exams
CHANGE COLUMN Exam_Building Exam_Location varchar(10) NOT NULL;

ALTER TABLE Exams
ADD COLUMN Proctor_Email VARCHAR(100) NOT NULL AFTER Exam_Location;


-- North: Devin for CIT 129, CIT 130, CS 135
UPDATE Exams
SET Proctor_Email = 'devin.ibarra@csn.edu'
WHERE Exam_Campus = 'North'
  AND Exam_Name IN ('CIT 129', 'CIT 130', 'CS 135');

-- North: Eddie for CIT 131, CSCO 120, GRC 101
UPDATE Exams
SET Proctor_Email = 'eddie.ali@csn.edu'
WHERE Exam_Campus = 'North'
  AND Exam_Name IN ('CIT 131', 'CSCO 120', 'GRC 101');

-- West: Edward for CIT 129, CIT 130, CS 135
UPDATE Exams
SET Proctor_Email = 'edward.hart@csn.edu'
WHERE Exam_Campus = 'West'
  AND Exam_Name IN ('CIT 129', 'CIT 130', 'CS 135');

-- West: Jamie for CIT 131, CSCO 120, GRC 101
UPDATE Exams
SET Proctor_Email = 'jamie.herman@csn.edu'
WHERE Exam_Campus = 'West'
  AND Exam_Name IN ('CIT 131', 'CSCO 120', 'GRC 101');
  
  -- Henderson: Lily for CIT 129, CIT 130, CS 135
UPDATE Exams
SET Proctor_Email = 'lily.flores@csn.edu'
WHERE Exam_Campus = 'Henderson'
  AND Exam_Name IN ('CIT 129', 'CIT 130', 'CS 135');

-- Henderson: Coen for CIT 131, CSCO 120, GRC 101
UPDATE Exams
SET Proctor_Email = 'coen.ray@csn.edu'
WHERE Exam_Campus = 'Henderson'
  AND Exam_Name IN ('CIT 131', 'CSCO 120', 'GRC 101');
  
  
