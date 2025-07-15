from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from functools import wraps

class IsAdminUser(BasePermission):
    """
    管理员权限检查 - 包括管理员和超级管理员
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_staff
        )

class IsSuperUser(BasePermission):
    """
    超级管理员权限检查 - 仅超级管理员
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser

class IsReadOnlyUser(BasePermission):
    """
    只读权限检查 - 普通用户只能查看
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # 管理员和超级管理员有所有权限
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # 普通用户只能进行GET请求
        return request.method in ['GET', 'HEAD', 'OPTIONS']

def superuser_required(view_func):
    """
    超级管理员权限装饰器
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'error': '请先登录'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not request.user.is_superuser:
            return Response({
                'error': '权限不足，需要超级管理员权限'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return view_func(self, request, *args, **kwargs)
    return wrapper

def get_user_permissions(user):
    """
    获取用户权限配置
    """
    if not user.is_authenticated:
        return {
            'can_view': False,
            'can_add': False,
            'can_edit': False,
            'can_delete': False,
            'can_import': False,
            'can_export': False,
            'can_manage_users': False,
            'is_admin': False,
            'is_superuser': False,
            'user_role': 'guest'
        }
    
    is_staff = user.is_staff
    is_superuser = user.is_superuser
    is_admin = is_staff or is_superuser
    
    return {
        # 基础权限
        'can_view': True,  # 所有登录用户都可以查看
        'can_export': True,  # 所有登录用户都可以导出
        
        # 管理员权限（管理员和超级管理员都有）
        'can_add': is_admin,
        'can_edit': is_admin,
        'can_delete': is_admin,
        'can_import': is_admin,
        
        # 超级管理员专有权限
        'can_manage_users': is_superuser,  # 只有超级管理员可以管理用户
        'can_manage_system': is_superuser,  # 系统设置等高级功能
        
        # 角色标识
        'is_admin': is_admin,
        'is_superuser': is_superuser,
        'user_role': 'superuser' if is_superuser else ('admin' if is_staff else 'user')
    } 