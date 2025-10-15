
CREATE DATABASE IF NOT EXISTS student_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE student_db;


CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  roll VARCHAR(50) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  age INT,
  gender VARCHAR(10),
  course VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


INSERT INTO students (roll, name, age, gender, course) VALUES
('101', 'Rahul Kulkarni', 20, 'Male', 'BCA'),
('102', 'Sneha Patil', 21, 'Female', 'BSc CS'),
('103', 'Amit Sharma', 22, 'Male', 'B.Tech CSE');
