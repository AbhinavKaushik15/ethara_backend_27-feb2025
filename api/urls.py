from django.urls import path
from . import views

urlpatterns = [
    # Employee routes
    path('employees/', views.employee_list, name='employee-list'),
    path('employees/<str:id>/', views.employee_detail, name='employee-detail'),
    
    # Attendance routes
    path('attendance/', views.attendance_list, name='attendance-list'),
    path('attendance/<str:employee_id>/', views.attendance_by_employee, name='attendance-by-employee'),
    
    # Dashboard routes
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]
