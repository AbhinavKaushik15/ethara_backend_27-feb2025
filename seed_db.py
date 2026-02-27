import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_backend.settings')
django.setup()

from api.models import Employee, Attendance
from datetime import datetime, timedelta
import random

def seed_data():
    print("Seeding database...")
    
    # 1. Clear existing data
    Employee.objects.all().delete()
    Attendance.objects.all().delete()
    
    # 2. Create sample employees
    depts = ['Engineering', 'HR', 'Sales', 'Finance', 'Marketing', 'Operations']
    employees_data = [
        {"name": "Abhinav Kaushik", "email": "abhinav@example.com", "dept": "Engineering"},
        {"name": "John Doe", "email": "john@example.com", "dept": "Sales"},
        {"name": "Jane Smith", "email": "jane@example.com", "dept": "HR"},
        {"name": "Mike Ross", "email": "mike@example.com", "dept": "Finance"},
        {"name": "Harvey Specter", "email": "harvey@example.com", "dept": "Operations"},
    ]
    
    created_employees = []
    for i, emp_info in enumerate(employees_data):
        emp_id = f"EMP{100 + i}"
        emp = Employee.objects.create(
            employee_id=emp_id,
            full_name=emp_info["name"],
            email=emp_info["email"],
            department=emp_info["dept"]
        )
        created_employees.append(emp)
        print(f"Created employee: {emp.full_name} ({emp.employee_id})")
        
    # 3. Create dummy attendance for the last 7 days
    today = datetime.now().date()
    for day_offset in range(7):
        date = today - timedelta(days=day_offset)
        for emp in created_employees:
            status = "Present" if random.random() > 0.2 else "Absent"
            Attendance.objects.create(
                employee=emp,
                date=date,
                status=status
            )
    
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
