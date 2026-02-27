from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Max
from .models import Employee, Attendance
from .serializers import EmployeeSerializer, AttendanceSerializer
from datetime import datetime

# Employee Views
@api_view(['GET', 'POST'])
def employee_list(req):
    if req.method == 'GET':
        employees = Employee.objects.all().order_by('-created_at')
        serializer = EmployeeSerializer(employees, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

    elif req.method == 'POST':
        name = req.data.get('name')
        email = req.data.get('email', '').lower()
        department = req.data.get('department')

        if not name or not email or not department:
            return Response({
                "success": False,
                "message": "Name, email, and department are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if Employee.objects.filter(email=email).exists():
            return Response({
                "success": False,
                "message": "Email already exists"
            }, status=status.HTTP_409_CONFLICT)

        # Generate employeeId (EMP001, EMP002, etc.)
        last_employee = Employee.objects.all().order_by('-employee_id').first()
        if last_employee and last_employee.employee_id:
            try:
                last_number = int(last_employee.employee_id.replace('EMP', ''))
                employee_id = f"EMP{str(last_number + 1).zfill(3)}"
            except ValueError:
                employee_id = "EMP001"
        else:
            employee_id = "EMP001"

        employee = Employee.objects.create(
            employee_id=employee_id,
            full_name=name,
            email=email,
            department=department
        )
        serializer = EmployeeSerializer(employee)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def employee_detail(req, id):
    try:
        employee = Employee.objects.get(employee_id=id)
    except Employee.DoesNotExist:
        return Response({
            "success": False,
            "message": "Employee not found"
        }, status=status.HTTP_404_NOT_FOUND)

    if req.method == 'GET':
        serializer = EmployeeSerializer(employee)
        return Response({
            "success": True,
            "data": serializer.data
        })

    elif req.method == 'PUT':
        name = req.data.get('name')
        email = req.data.get('email')
        department = req.data.get('department')

        if email:
            email = email.lower()
            if Employee.objects.filter(email=email).exclude(employee_id=id).exists():
                return Response({
                    "success": False,
                    "message": "Email already exists"
                }, status=status.HTTP_409_CONFLICT)
            employee.email = email

        if name:
            employee.full_name = name
        if department:
            employee.department = department
        
        employee.save()
        serializer = EmployeeSerializer(employee)
        return Response({
            "success": True,
            "data": serializer.data
        })

    elif req.method == 'DELETE':
        employee.delete()
        return Response({
            "success": True,
            "message": "Employee deleted successfully",
            "data": {"id": id}
        })

# Attendance Views
@api_view(['GET', 'POST'])
def attendance_list(req):
    if req.method == 'GET':
        date_str = req.query_params.get('date')
        query = Attendance.objects.all()
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                query = query.filter(date=date_obj)
            except ValueError:
                pass
        
        query = query.order_by('-date', '-created_at')
        serializer = AttendanceSerializer(query, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

    elif req.method == 'POST':
        employee_id = req.data.get('employeeId')
        date_str = req.data.get('date')
        att_status = req.data.get('status')

        if not employee_id or not date_str or not att_status:
            return Response({
                "success": False,
                "message": "Employee ID, date, and status are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if att_status not in ['Present', 'Absent']:
            return Response({
                "success": False,
                "message": 'Status must be either "Present" or "Absent"'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(employee_id=employee_id)
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (Employee.DoesNotExist, ValueError):
            return Response({
                "success": False,
                "message": "Employee not found or invalid date"
            }, status=status.HTTP_404_NOT_FOUND)

        attendance, created = Attendance.objects.update_or_create(
            employee=employee,
            date=date_obj,
            defaults={'status': att_status}
        )

        serializer = AttendanceSerializer(attendance)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['GET'])
def attendance_by_employee(req, employee_id):
    try:
        employee = Employee.objects.get(employee_id=employee_id)
        attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')
        serializer = AttendanceSerializer(attendance_records, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })
    except Employee.DoesNotExist:
        return Response({
            "success": False,
            "message": "Employee not found"
        }, status=status.HTTP_404_NOT_FOUND)

# Dashboard Views
@api_view(['GET'])
def dashboard_stats(req):
    total_employees = Employee.objects.count()
    
    # Simple logic for today's attendance
    today = datetime.now().date()
    today_attendance = Attendance.objects.filter(date=today)
    present_today = today_attendance.filter(status='Present').count()
    absent_today = today_attendance.filter(status='Absent').count()
    
    # Calculate attendance rate
    attendance_rate = 0
    if total_employees > 0:
        attendance_rate = round((present_today / total_employees) * 100, 2)

    # Weekly trend (last 7 days)
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekly_trend = [{"day": day, "present": 0} for day in days]
    
    # Department distribution
    departments = Employee.objects.values('department').annotate(count=Count('id'))
    dept_distribution = [{"name": d['department'], "value": d['count']} for d in departments]

    return Response({
        "success": True,
        "data": {
            "totalEmployees": total_employees,
            "presentToday": present_today,
            "absentToday": absent_today,
            "attendanceRate": attendance_rate,
            "totalDepartments": len(dept_distribution),
            "weeklyTrend": weekly_trend,
            "departmentDistribution": dept_distribution,
            "todayAttendanceStatus": [
                {"name": "Present", "count": present_today},
                {"name": "Absent", "count": absent_today}
            ]
        }
    })
