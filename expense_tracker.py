from datetime import datetime
import mysql.connector

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sathwik@4036",
    database="expense_tracker"
)

cursor = db.cursor()


def add_expense():
    # Date validation
    while True:
        date = input("Enter date (YYYY-MM-DD): ")
        try:
            datetime.strptime(date, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date! Please use YYYY-MM-DD.")

    category = input("Enter category: ").strip()

    # Amount validation
    while True:
        try:
            amount = float(input("Enter amount: "))
            if amount <= 0:
                print("Amount must be greater than 0.")
                continue
            break
        except ValueError:
            print("Please enter a valid amount.")

    description = input("Enter description: ").strip()


    sql = """
    INSERT INTO expenses (date, category, amount, description)
    VALUES (%s, %s, %s, %s)
    """

    values = (date, category, amount, description)

    cursor.execute(sql, values)
    db.commit()

    print(" Expense added successfully!")


def view_expenses():
    cursor.execute("SELECT id, date, category, amount, description FROM expenses")
    records = cursor.fetchall()

    print("\n--- All Expenses ---")

    if not records:
        print("No expenses found.")
        return

    # Formatted display
    print(f"{'ID':<5} | {'Date':<12} | {'Category':<15} | {'Amount':<10} | {'Description'}")
    print("-" * 60)
    for row in records:
        print(f"{row[0]:<5} | {str(row[1]):<12} | {row[2]:<15} | ${row[3]:<9.2f} | {row[4]}")


def category_report():
    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

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
    cursor.execute("""
    SELECT category, SUM(amount) AS total
    FROM expenses
    GROUP BY category
    ORDER BY total DESC
    LIMIT 1
    """)

    result = cursor.fetchone()

    print("\n--- Highest Spending Category ---")
    if result:
        print(f"Category: {result[0]}")
        print(f"Total Spent: ${result[1]:.2f}")
    else:
        print("No expenses found.")


# Main Loop
while True:
    print("\n===== Expense Tracker =====")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Category Report")
    print("4. Highest Spending Category")
    print("5. Exit")

    choice = input("Enter choice: ").strip()

    if choice == "1":
        add_expense()

    elif choice == "2":
        view_expenses()

    elif choice == "3":
        category_report()

    elif choice == "4":
        highest_category()

    elif choice == "5":
        print("Goodbye!")
        cursor.close()
        db.close()
        break

    else:
        print("Invalid choice, please select 1-5.")