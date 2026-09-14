# Expense Tracker

A CLI-based Expense Tracker built with Python and MySQL to record, track, and analyze personal spending.

## Features
- **Add Expenses:** Log dates, categories, amounts, and descriptions with input validation.
- **View Records:** Display all logged transactions in a clean table format.
- **Edit/Delete Records:** Update or remove existing expense records by ID.
- **Search and Filter:** Find expenses by category, date, or amount range.
- **Date Reports:** Review spending across custom date ranges or by month.
- **Budget Alerts:** Set monthly budgets and receive warnings when spending crosses the limit.
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

CREATE TABLE budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    month_key VARCHAR(7) NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL
);
```

## Environment Setup
Create a `.env` file with your MySQL connection details:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=expense_tracker
```
