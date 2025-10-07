CREATE TABLE Registrations (
  Registration_ID VARCHAR(12) PRIMARY KEY,      
  User_ID         INT NOT NULL,                
  Exam_ID         VARCHAR(20) NOT NULL,             
  status          ENUM('active','cancelled','completed','no_show')
                  NOT NULL DEFAULT 'active',
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_no_duplicate (User_ID, Exam_ID),    -- no double-booking same exam
  FOREIGN KEY (User_ID) REFERENCES Users(User_ID),
  FOREIGN KEY (Exam_ID) REFERENCES Exams(Exam_ID)
);

DELIMITER $$
CREATE TRIGGER trg_Registration_ID
BEFORE INSERT ON Registrations
FOR EACH ROW
BEGIN
  DECLARE next_id INT;
  SELECT IFNULL(MAX(CAST(SUBSTRING(Registration_ID,2) AS UNSIGNED)),0) + 1
    INTO next_id
    FROM Registrations;
  SET NEW.Registration_ID = CONCAT('R', LPAD(next_id, 5, '0')); -- R00001, R00002, ...
END$$
DELIMITER ;