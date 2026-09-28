"""
Seed script: creates the initial data needed to actually use the system,
since employees cannot self-register.

Run with:  python -m app.utils.seed
"""
import os
from datetime import date
from app.core.enums import Role
from app.core.config import settings
from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_type import LeaveType
from app.models.leave_balance import LeaveBalance
from app.models.holiday import Holiday


def seed(default_password: str = None, update_passwords: bool = False):
    if default_password is None:
        default_password = settings.DEFAULT_DEV_PASSWORD

    db = SessionLocal()
    try:
        current_year = date.today().year

        # --- 1. Departments ---
        dept_data = [
            ("Engineering", "Product engineering, software development, and technology operations"),
            ("HR", "Human resources, talent acquisition, and people operations"),
            ("Finance", "Finance, accounting, auditing, and corporate budgeting"),
            ("Operations", "Business operations, infrastructure, and facilities management"),
        ]
        departments = {}
        for name, desc in dept_data:
            dept = db.query(Department).filter(Department.name == name).first()
            if not dept:
                dept = Department(name=name, description=desc)
                db.add(dept)
                db.commit()
                db.refresh(dept)
            departments[name] = dept

        engineering = departments["Engineering"]
        hr_dept = departments["HR"]
        finance = departments["Finance"]
        operations = departments["Operations"]

        # --- 2. Leave Types ---
        leave_type_defs = [
            ("Paid Leave", "Standard paid annual leave allowance", True),
            ("Sick Leave", "Paid leave for health and medical reasons", True),
            ("Casual Leave", "Paid leave for personal and urgent matters", True),
            ("Unpaid Leave", "Unpaid leave of absence without compensation", False),
        ]
        leave_types = {}
        for name, desc, is_paid in leave_type_defs:
            lt = db.query(LeaveType).filter(LeaveType.name == name).first()
            if not lt:
                lt = LeaveType(name=name, description=desc, is_paid=is_paid, is_active=True)
                db.add(lt)
                db.commit()
                db.refresh(lt)
            leave_types[name] = lt

        # --- 3. Employee Helper ---
        def get_or_create_employee(name, email, password, role, department, manager=None, is_admin=False):
            emp = db.query(Employee).filter(Employee.email == email.lower()).first()
            if emp:
                if update_passwords:
                    emp.password_hash = hash_password(password)
                    db.commit()
                return emp
            emp = Employee(
                name=name,
                email=email.lower(),
                password_hash=hash_password(password),
                role=role,
                department_id=department.id if department else None,
                manager_id=manager.id if manager else None,
                is_admin=is_admin,
                is_active=True,
            )
            db.add(emp)
            db.commit()
            db.refresh(emp)
            return emp

        # --- 4. Business Hierarchy (Engineering & Executive) ---
        # CEO -> Director -> Senior Manager -> Manager -> Team Lead -> Employee
        ceo = get_or_create_employee(
            "Carol CEO", "ceo@company.com", default_password, Role.CEO, engineering
        )
        director = get_or_create_employee(
            "Dan Director", "director@company.com", default_password, Role.DIRECTOR, engineering, manager=ceo
        )
        sr_manager = get_or_create_employee(
            "Sara SeniorManager", "seniormanager@company.com", default_password, Role.SENIOR_MANAGER, engineering, manager=director
        )
        manager = get_or_create_employee(
            "Mike Manager", "manager@company.com", default_password, Role.MANAGER, engineering, manager=sr_manager
        )
        team_lead = get_or_create_employee(
            "Tom TeamLead", "teamlead@company.com", default_password, Role.TEAM_LEAD, engineering, manager=manager
        )
        employee = get_or_create_employee(
            "Emma Employee", "employee@company.com", default_password, Role.EMPLOYEE, engineering, manager=team_lead
        )

        # --- 5. HR Hierarchy ---
        # CEO -> HR Director -> HR Manager -> HR Executive / HR Associate
        hr_director = get_or_create_employee(
            "Helen HRDirector", "hrdirector@company.com", default_password, Role.HR_DIRECTOR, hr_dept, manager=ceo
        )
        hr_manager = get_or_create_employee(
            "Harry HRManager", "hrmanager@company.com", default_password, Role.HR_MANAGER, hr_dept, manager=hr_director
        )
        hr_executive = get_or_create_employee(
            "Henry HRExecutive", "hrexecutive@company.com", default_password, Role.HR_EXECUTIVE, hr_dept, manager=hr_manager
        )
        hr_associate = get_or_create_employee(
            "Holly HRAssociate", "hrassociate@company.com", default_password, Role.HR_ASSOCIATE, hr_dept, manager=hr_manager
        )

        # --- 6. Admin & Other Departments ---
        admin = get_or_create_employee(
            "Alice Admin", "admin@company.com", default_password, Role.ADMIN, hr_dept, manager=ceo, is_admin=True
        )
        finance_emp = get_or_create_employee(
            "Frank Finance", "finance@company.com", default_password, Role.EMPLOYEE, finance, manager=manager
        )
        operations_emp = get_or_create_employee(
            "Oscar Operations", "operations@company.com", default_password, Role.EMPLOYEE, operations, manager=manager
        )

        all_seeded_employees = [
            ceo, director, sr_manager, manager, team_lead, employee,
            hr_director, hr_manager, hr_executive, hr_associate,
            admin, finance_emp, operations_emp
        ]

        # --- 7. Leave Balances for all employees ---
        balance_allocations = [
            ("Paid Leave", 18.0),
            ("Sick Leave", 12.0),
            ("Casual Leave", 10.0),
            ("Unpaid Leave", 0.0),
        ]

        for emp in all_seeded_employees:
            for lt_name, total in balance_allocations:
                lt = leave_types[lt_name]
                existing_bal = (
                    db.query(LeaveBalance)
                    .filter(
                        LeaveBalance.employee_id == emp.id,
                        LeaveBalance.leave_type_id == lt.id,
                        LeaveBalance.year == current_year,
                    )
                    .first()
                )
                if not existing_bal:
                    # Give Emma Employee a realistic initial used balance of 2 days Paid Leave
                    used = 2.0 if (emp.id == employee.id and lt_name == "Paid Leave") else 0.0
                    bal = LeaveBalance(
                        employee_id=emp.id,
                        leave_type_id=lt.id,
                        year=current_year,
                        total_days=total,
                        used_days=used,
                    )
                    db.add(bal)
        db.commit()

        # --- 8. Holidays (Sample company holidays) ---
        holiday_defs = [
            (date(current_year, 1, 1), "New Year's Day"),
            (date(current_year, 1, 26), "Republic Day"),
            (date(current_year, 5, 1), "Labor Day"),
            (date(current_year, 8, 15), "Independence Day"),
            (date(current_year, 10, 2), "Gandhi Jayanti"),
            (date(current_year, 12, 25), "Christmas Day"),
        ]
        for hdate, hname in holiday_defs:
            existing_h = db.query(Holiday).filter(Holiday.holiday_date == hdate).first()
            if not existing_h:
                db.add(Holiday(holiday_date=hdate, name=hname, is_active=True))
        db.commit()

        print(f"Seed data created successfully for year {current_year}.")
        print(f"Sample Development Accounts (Default dev password: {default_password}):")
        print(f"{'Role':20s} {'Email':32s} {'Department':15s} Admin")
        print("-" * 75)
        for e in all_seeded_employees:
            dept_name = e.department.name if e.department else "None"
            print(f"{e.role:20s} {e.email:32s} {dept_name:15s} {e.is_admin}")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed the database with sample accounts and initial data.")
    parser.add_argument(
        "--password",
        default=os.getenv("DEFAULT_DEV_PASSWORD", "Password123"),
        help="Default password for seeded accounts (default: env DEFAULT_DEV_PASSWORD or Password123)",
    )
    parser.add_argument(
        "--update-passwords",
        action="store_true",
        default=os.getenv("UPDATE_PASSWORDS", "false").lower() in ("true", "1", "yes"),
        help="Update password hashes for existing sample accounts to match the default password",
    )
    args = parser.parse_args()
    seed(default_password=args.password, update_passwords=args.update_passwords)
