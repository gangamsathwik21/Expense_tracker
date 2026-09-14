from datetime import datetime
from decimal import Decimal
import os

import mysql.connector

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "expense_tracker"),
)

cursor = db.cursor()


def setup_database():
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS budgets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            month_key VARCHAR(7) NOT NULL UNIQUE,
            amount DECIMAL(10,2) NOT NULL
        )
        """
    )
    db.commit()


def input_date(prompt):
    while True:
        date_value = input(prompt).strip()
        try:
            datetime.strptime(date_value, "%Y-%m-%d")
            return date_value
        except ValueError:
            print("Invalid date! Please use YYYY-MM-DD.")


def input_month(prompt):
    while True:
        month_value = input(prompt).strip()
        try:
            datetime.strptime(month_value, "%Y-%m")
            return month_value
        except ValueError:
            print("Invalid month! Please use YYYY-MM.")


def input_amount(prompt):
    while True:
        try:
            amount = Decimal(input(prompt).strip())
            if amount <= 0:
                print("Amount must be greater than 0.")
                continue
            return amount
        except Exception:
            print("Please enter a valid amount.")


def display_expenses(records, title):
    print(f"\n--- {title} ---")

    if not records:
        print("No expenses found.")
        return

    print(f"{'ID':<5} | {'Date':<12} | {'Category':<15} | {'Amount':<10} | {'Description'}")
    print("-" * 70)
    for row in records:
        print(f"{row[0]:<5} | {str(row[1]):<12} | {row[2]:<15} | ${row[3]:<9.2f} | {row[4] or ''}")


def check_budget_warning(month_key):
    cursor.execute("SELECT amount FROM budgets WHERE month_key = %s", (month_key,))
    budget = cursor.fetchone()

    if not budget:
        return

    cursor.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE DATE_FORMAT(date, '%Y-%m') = %s
        """,
        (month_key,),
    )
    total_spent = cursor.fetchone()[0]

    if total_spent > budget[0]:
        print(f"Warning: spending for {month_key} is ${total_spent:.2f}, above the ${budget[0]:.2f} budget.")
    else:
        remaining = budget[0] - total_spent
        print(f"Budget status for {month_key}: ${remaining:.2f} remaining.")


def add_expense():
    date = input_date("Enter date (YYYY-MM-DD): ")
    category = input("Enter category: ").strip()
    amount = input_amount("Enter amount: ")
    description = input("Enter description: ").strip()

    cursor.execute(
        """
        INSERT INTO expenses (date, category, amount, description)
        VALUES (%s, %s, %s, %s)
        """,
        (date, category, amount, description),
    )
    db.commit()

    print("Expense added successfully!")
    check_budget_warning(date[:7])


def view_expenses():
    cursor.execute("SELECT id, date, category, amount, description FROM expenses ORDER BY date DESC, id DESC")
    display_expenses(cursor.fetchall(), "All Expenses")


def get_expense(expense_id):
    cursor.execute(
        "SELECT id, date, category, amount, description FROM expenses WHERE id = %s",
        (expense_id,),
    )
    return cursor.fetchone()


def edit_expense():
    expense_id = input("Enter expense ID to edit: ").strip()
    expense = get_expense(expense_id)

    if not expense:
        print("Expense not found.")
        return

    print("Press Enter to keep the current value.")
    new_date = input(f"Date [{expense[1]}]: ").strip()
    if new_date:
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date! Edit cancelled.")
            return
    else:
        new_date = str(expense[1])

    new_category = input(f"Category [{expense[2]}]: ").strip() or expense[2]
    new_amount_text = input(f"Amount [{expense[3]:.2f}]: ").strip()
    if new_amount_text:
        try:
            new_amount = Decimal(new_amount_text)
            if new_amount <= 0:
                print("Amount must be greater than 0. Edit cancelled.")
                return
        except Exception:
            print("Invalid amount! Edit cancelled.")
            return
    else:
        new_amount = expense[3]

    new_description = input(f"Description [{expense[4] or ''}]: ").strip() or expense[4]

    cursor.execute(
        """
        UPDATE expenses
        SET date = %s, category = %s, amount = %s, description = %s
        WHERE id = %s
        """,
        (new_date, new_category, new_amount, new_description, expense_id),
    )
    db.commit()

    print("Expense updated successfully!")
    check_budget_warning(new_date[:7])


def delete_expense():
    expense_id = input("Enter expense ID to delete: ").strip()
    expense = get_expense(expense_id)

    if not expense:
        print("Expense not found.")
        return

    confirm = input(f"Delete expense {expense_id}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Delete cancelled.")
        return

    cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
    db.commit()
    print("Expense deleted successfully!")


def category_report():
    cursor.execute(
        """
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
        ORDER BY SUM(amount) DESC
        """
    )

    records = cursor.fetchall()

    print("\n--- Category Report ---")

    if not records:
        print("No expenses found.")
        return

    print(f"{'Category':<20} | {'Total Spent'}")
    print("-" * 35)
    for row in records:
        print(f"{row[0]:<20} | ${row[1]:.2f}")


def highest_category():
    cursor.execute(
        """
        SELECT category, SUM(amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
        LIMIT 1
        """
    )

    result = cursor.fetchone()

    print("\n--- Highest Spending Category ---")
    if result:
        print(f"Category: {result[0]}")
        print(f"Total Spent: ${result[1]:.2f}")
    else:
        print("No expenses found.")


def date_range_report():
    start_date = input_date("Enter start date (YYYY-MM-DD): ")
    end_date = input_date("Enter end date (YYYY-MM-DD): ")

    if start_date > end_date:
        print("Start date cannot be after end date.")
        return

    cursor.execute(
        """
        SELECT id, date, category, amount, description
        FROM expenses
        WHERE date BETWEEN %s AND %s
        ORDER BY date DESC, id DESC
        """,
        (start_date, end_date),
    )
    records = cursor.fetchall()
    display_expenses(records, f"Expenses from {start_date} to {end_date}")

    cursor.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE date BETWEEN %s AND %s
        """,
        (start_date, end_date),
    )
    print(f"Total spent: ${cursor.fetchone()[0]:.2f}")


def monthly_report():
    month_key = input_month("Enter month (YYYY-MM): ")
    cursor.execute(
        """
        SELECT category, SUM(amount)
        FROM expenses
        WHERE DATE_FORMAT(date, '%Y-%m') = %s
        GROUP BY category
        ORDER BY SUM(amount) DESC
        """,
        (month_key,),
    )
    records = cursor.fetchall()

    print(f"\n--- Monthly Report: {month_key} ---")
    if not records:
        print("No expenses found for this month.")
        return

    print(f"{'Category':<20} | {'Total Spent'}")
    print("-" * 35)
    for row in records:
        print(f"{row[0]:<20} | ${row[1]:.2f}")

    check_budget_warning(month_key)


def set_monthly_budget():
    month_key = input_month("Enter month for budget (YYYY-MM): ")
    amount = input_amount("Enter monthly budget amount: ")

    cursor.execute(
        """
        INSERT INTO budgets (month_key, amount)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE amount = VALUES(amount)
        """,
        (month_key, amount),
    )
    db.commit()

    print("Budget saved successfully!")
    check_budget_warning(month_key)


def search_expenses():
    print("\n--- Search Expenses ---")
    print("1. Search by category")
    print("2. Search by date")
    print("3. Search by amount range")

    choice = input("Enter choice: ").strip()

    if choice == "1":
        category = input("Enter category keyword: ").strip()
        cursor.execute(
            """
            SELECT id, date, category, amount, description
            FROM expenses
            WHERE category LIKE %s
            ORDER BY date DESC, id DESC
            """,
            (f"%{category}%",),
        )
        display_expenses(cursor.fetchall(), f"Category Search: {category}")
    elif choice == "2":
        date = input_date("Enter date (YYYY-MM-DD): ")
        cursor.execute(
            """
            SELECT id, date, category, amount, description
            FROM expenses
            WHERE date = %s
            ORDER BY id DESC
            """,
            (date,),
        )
        display_expenses(cursor.fetchall(), f"Date Search: {date}")
    elif choice == "3":
        min_amount = input_amount("Enter minimum amount: ")
        max_amount = input_amount("Enter maximum amount: ")
        if min_amount > max_amount:
            print("Minimum amount cannot be greater than maximum amount.")
            return
        cursor.execute(
            """
            SELECT id, date, category, amount, description
            FROM expenses
            WHERE amount BETWEEN %s AND %s
            ORDER BY amount DESC
            """,
            (min_amount, max_amount),
        )
        display_expenses(cursor.fetchall(), f"Amount Search: ${min_amount:.2f} to ${max_amount:.2f}")
    else:
        print("Invalid choice.")


def main():
    setup_database()

    while True:
        print("\n===== Expense Tracker =====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Edit Expense")
        print("4. Delete Expense")
        print("5. Search/Filter Expenses")
        print("6. Category Report")
        print("7. Date Range Report")
        print("8. Monthly Report")
        print("9. Set Monthly Budget")
        print("10. Highest Spending Category")
        print("11. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            edit_expense()
        elif choice == "4":
            delete_expense()
        elif choice == "5":
            search_expenses()
        elif choice == "6":
            category_report()
        elif choice == "7":
            date_range_report()
        elif choice == "8":
            monthly_report()
        elif choice == "9":
            set_monthly_budget()
        elif choice == "10":
            highest_category()
        elif choice == "11":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please select 1-11.")


if __name__ == "__main__":
    try:
        main()
    finally:
        cursor.close()
        db.close()
