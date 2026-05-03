CREATE TABLE trains (
  id INT PRIMARY KEY,
  speed FLOAT,
  position FLOAT,
  status VARCHAR(50)
);

CREATE TABLE ai_decisions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  train_id INT,
  recommendation VARCHAR(255),
  confidence FLOAT,
  timestamp DATETIME
);

CREATE TABLE operator_actions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  train_id INT,
  action VARCHAR(255),
  timestamp DATETIME
);
