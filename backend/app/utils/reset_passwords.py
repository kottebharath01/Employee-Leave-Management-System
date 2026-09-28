"""
Utility script to reset password for all sample/employee accounts in the database.

Usage:
    # Reset all employee accounts to a new password:
    python -m app.utils.reset_passwords "MyNewPassword"

    # Reset a specific account by email:
    python -m app.utils.reset_passwords "MyNewPassword" --email admin@company.com

    # Interactive prompt (doesn't expose password in terminal history):
    python -m app.utils.reset_passwords
"""
import sys
import getpass
import argparse
from app.database.session import SessionLocal
from app.models.employee import Employee
from app.core.security import hash_password


def reset_passwords(new_password: str, email: str | None = None) -> int:
    if not new_password:
        print("Error: Password cannot be empty.")
        return 0

    db = SessionLocal()
    try:
        query = db.query(Employee)
        if email:
            query = query.filter(Employee.email == email.lower().strip())
            employees = query.all()
            if not employees:
                print(f"No employee found with email: {email}")
                return 0
        else:
            employees = query.all()
            if not employees:
                print("No employee accounts found in the database. Have you run seed?")
                return 0

        hashed = hash_password(new_password)
        for emp in employees:
            emp.password_hash = hashed

        db.commit()

        print(f"Successfully updated password for {len(employees)} account(s)!")
        print(f"{'Role':20s} {'Email':32s} {'Name':20s}")
        print("-" * 75)
        for emp in employees:
            print(f"{emp.role:20s} {emp.email:32s} {emp.name:20s}")
        return len(employees)
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Reset password for employee accounts.")
    parser.add_argument("password", nargs="?", default=None, help="The new password to set")
    parser.add_argument("--email", default=None, help="Optional email to reset a single account")
    args = parser.parse_args()

    password = args.password
    if not password:
        password = getpass.getpass("Enter new password for accounts: ")
        confirm = getpass.getpass("Confirm new password: ")
        if password != confirm:
            print("Error: Passwords do not match.")
            sys.exit(1)

    reset_passwords(password, email=args.email)


if __name__ == "__main__":
    main()
