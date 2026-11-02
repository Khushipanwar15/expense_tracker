"""
Expense Tracker - a simple command-line app built with Python and SQLite.

Features:
  1. Add an expense
  2. View all expenses
  3. Delete an expense
  4. Category-wise summary (data processing with SQL)
  5. Monthly total
"""

import sqlite3
from datetime import date, datetime


class ExpenseTracker:
    """Handles all database operations for expenses (OOP: one class, many methods)."""

    def __init__(self, db_name="expenses.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            expense_date TEXT NOT NULL
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_expense(self, amount, category, description, expense_date):
        query = """
        INSERT INTO expenses (amount, category, description, expense_date)
        VALUES (?, ?, ?, ?)
        """
        self.conn.execute(query, (amount, category, description, expense_date))
        self.conn.commit()

    def get_all_expenses(self):
        cursor = self.conn.execute(
            "SELECT id, expense_date, category, amount, description "
            "FROM expenses ORDER BY expense_date DESC, id DESC"
        )
        return cursor.fetchall()

    def delete_expense(self, expense_id):
        cursor = self.conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return cursor.rowcount > 0  # True if a row was deleted

    def category_summary(self):
        cursor = self.conn.execute(
            "SELECT category, SUM(amount) AS total, COUNT(*) AS count "
            "FROM expenses GROUP BY category ORDER BY total DESC"
        )
        return cursor.fetchall()

    def monthly_total(self, year_month):
        """year_month format: 'YYYY-MM'"""
        cursor = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses "
            "WHERE strftime('%Y-%m', expense_date) = ?",
            (year_month,),
        )
        return cursor.fetchone()[0]

    def close(self):
        self.conn.close()


# ---------- Helper functions for user input ----------

def read_amount():
    while True:
        try:
            amount = float(input("Amount: "))
            if amount <= 0:
                print("Amount must be greater than 0.")
                continue
            return amount
        except ValueError:
            print("Please enter a valid number.")


def read_date():
    while True:
        value = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
        if value == "":
            return date.today().isoformat()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")


def print_expenses(expenses):
    if not expenses:
        print("\nNo expenses found.")
        return
    print(f"\n{'ID':<5}{'Date':<13}{'Category':<15}{'Amount':>10}  Description")
    print("-" * 60)
    for exp_id, exp_date, category, amount, description in expenses:
        print(f"{exp_id:<5}{exp_date:<13}{category:<15}{amount:>10.2f}  {description}")


def show_menu():
    print("\n===== EXPENSE TRACKER =====")
    print("1. Add expense")
    print("2. View all expenses")
    print("3. Delete expense")
    print("4. Category-wise summary")
    print("5. Monthly total")
    print("6. Exit")


def main():
    tracker = ExpenseTracker()

    while True:
        show_menu()
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            amount = read_amount()
            category = input("Category (e.g. Food, Travel, Rent): ").strip().title() or "Other"
            description = input("Description: ").strip()
            expense_date = read_date()
            tracker.add_expense(amount, category, description, expense_date)
            print("Expense added successfully.")

        elif choice == "2":
            print_expenses(tracker.get_all_expenses())

        elif choice == "3":
            try:
                expense_id = int(input("Enter the ID to delete: "))
            except ValueError:
                print("Please enter a valid ID number.")
                continue
            if tracker.delete_expense(expense_id):
                print("Expense deleted.")
            else:
                print("No expense found with that ID.")

        elif choice == "4":
            summary = tracker.category_summary()
            if not summary:
                print("\nNo expenses found.")
            else:
                print(f"\n{'Category':<15}{'Total':>10}{'Count':>8}")
                print("-" * 33)
                for category, total, count in summary:
                    print(f"{category:<15}{total:>10.2f}{count:>8}")

        elif choice == "5":
            month = input("Month (YYYY-MM, press Enter for this month): ").strip()
            if month == "":
                month = date.today().strftime("%Y-%m")
            print(f"\nTotal spent in {month}: {tracker.monthly_total(month):.2f}")

        elif choice == "6":
            tracker.close()
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    main()
