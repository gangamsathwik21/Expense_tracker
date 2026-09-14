DROP DATABASE IF EXISTS expense_tracker;
CREATE DATABASE expense_tracker;
USE expense_tracker;

CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    month_key VARCHAR(7) NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL
);
