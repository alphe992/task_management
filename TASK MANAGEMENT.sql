CREATE DATABASE TaskManagement;
USE TaskManagement;

CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL
);

CREATE TABLE Tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL,
    user_id INT,
    status VARCHAR(50),
    due_date DATE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

INSERT INTO Users (username) VALUES
('John Doe'),
('Jane Smith');

INSERT INTO Tasks (task_name, user_id, status, due_date) VALUES
('Finish Report', 1, 'To Do', '2025-03-30'),
('Develop Feature', 2, 'In Progress', '2025-04-05');
