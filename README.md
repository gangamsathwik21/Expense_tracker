# Expense Tracker

A CLI-based Expense Tracker built with Python and MySQL to record, track, and analyze personal spending.

## Features
- **Add Expenses:** Log dates, categories, amounts, and descriptions with input validation.
- **View Records:** Display all logged transactions in a clean table format.
- **Category Summary:** Generate aggregate spending reports grouped by category.
- **Highest Spending Insight:** Instantly find your top expense category.
- **Secure Configuration:** Protects database credentials using environment variables.

## Tech Stack
- **Language:** Python 3
- **Database:** MySQL
- **Libraries:** `mysql-connector-python`, `python-dotenv`

## Database Setup
Run the `expense_tracker sql.sql` script in your SQL client to create the table schema:

```sql
CREATE DATABASE expense_tracker;
USE expense_tracker;

CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description VARCHAR(255)
);
