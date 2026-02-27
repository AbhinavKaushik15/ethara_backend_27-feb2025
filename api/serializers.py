from rest_framework import serializers
from .models import Employee, Attendance

class EmployeeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='employee_id')
    name = serializers.CharField(source='full_name')

    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'department', 'created_at']

class AttendanceSerializer(serializers.ModelSerializer):
    employeeId = serializers.CharField(source='employee.employee_id')
    date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = Attendance
        fields = ['id', 'employeeId', 'date', 'status']
