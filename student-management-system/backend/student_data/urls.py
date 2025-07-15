from django.urls import path
from . import views
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .permissions import IsAdminUser, IsReadOnlyUser, admin_required, get_user_permissions

User = get_user_model()

urlpatterns = [
    # 健康检查端点
    path('health/', views.health_check, name='health_check'),
    
    # CSRF Token获取端点
    path('csrf-token/', views.CSRFTokenView.as_view(), name='csrf_token'),
    
    # 认证相关接口
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/user/', views.UserInfoView.as_view(), name='user_info'),
    
    path('import/', views.StudentDataImportView.as_view(), name='student_import'),
    path('list/', views.StudentDataListView.as_view(), name='student_list'),
    path('logs/', views.ImportLogView.as_view(), name='import_logs'),
    path('delete/', views.StudentDataDeleteView.as_view(), name='student_delete'),
    path('update/<int:student_id>/', views.StudentDataUpdateView.as_view(), name='student_update'),
    path('detail/<int:student_id>/', views.StudentDataDetailView.as_view(), name='student_detail'),
    
    # 转学相关接口
    path('transfer/in/', views.TransferInView.as_view(), name='transfer_in'),
    path('transfer/out/', views.TransferOutView.as_view(), name='transfer_out'),
    path('transfer/records/', views.TransferRecordListView.as_view(), name='transfer_records'),
    path('transfer/records/<int:record_id>/', views.TransferRecordDetailView.as_view(), name='transfer_record_detail'),
    path('transfer/records/<int:record_id>/update/', views.TransferRecordUpdateView.as_view(), name='transfer_record_update'),
    
    # 仪表盘统计数据接口
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard_stats'),
    
    # 休学和复学相关
    path('student/suspend/', views.StudentSuspendView.as_view(), name='student_suspend'),
    path('student/resume/', views.StudentResumeView.as_view(), name='student_resume'),
    path('student/suspended/', views.SuspendedStudentsView.as_view(), name='suspended_students'),
    
    # 成绩管理相关接口
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('exams/', views.ExamListView.as_view(), name='exam_list'),
    path('grades/', views.GradeListView.as_view(), name='grade_list'),
    path('grades/create/', views.GradeCreateView.as_view(), name='grade_create'),
    path('grades/analysis/', views.GradeAnalysisView.as_view(), name='grade_analysis'),
    
    # 成绩管理 - 横向显示
    path('grades/matrix/', views.GradeMatrixView.as_view(), name='grade_matrix'),
    path('grades/matrix/export/', views.GradeMatrixExportView.as_view(), name='grade_matrix_export'),
    path('grades/matrix/template/', views.GradeMatrixTemplateView.as_view(), name='grade_matrix_template'),
    path('grades/matrix/import/', views.GradeMatrixImportView.as_view(), name='grade_matrix_import'),  # 新增
    
    # 权限相关接口
    path('auth/permissions/', views.UserPermissionsView.as_view(), name='user_permissions'),
    
    # 用户管理相关接口
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/toggle-status/', views.UserToggleStatusView.as_view(), name='user_toggle_status'),
]