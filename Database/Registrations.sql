CREATE TABLE Registrations (
  Registration_ID VARCHAR(12) PRIMARY KEY,      
  Student_Email   VARCHAR(100) NOT NULL,                
  Exam_ID         VARCHAR(20) NOT NULL,             
  status          ENUM('active','canceled','completed','no_show')
                  NOT NULL DEFAULT 'active',
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  
  CONSTRAINT fk_registrations_exam
    FOREIGN KEY (Exam_ID)
    REFERENCES Exams(Exam_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    
  CONSTRAINT uq_no_duplicate UNIQUE (Student_Email, Exam_ID)    -- no double-booking same exam 
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

