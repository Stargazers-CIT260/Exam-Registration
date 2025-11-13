CREATE TABLE Locations (
  Campus VARCHAR(20) NOT NULL,
  Building_Code VARCHAR(10) NOT NULL,
  PRIMARY KEY (Campus, Building_Code),
  FOREIGN KEY (Campus) REFERENCES Campuses(Campus)
);

INSERT INTO Locations (Campus, Building_Code) VALUES
('North','C101'),('North','C107'),('North','C118'),('North','C201'),
('West','C105'),('West','C109'),('West','C117'),('West','C211'),
('Henderson','C114'),('Henderson','C111'),('Henderson','C205'),('Henderson','C207');