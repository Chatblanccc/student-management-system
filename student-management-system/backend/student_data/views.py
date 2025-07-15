from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import pandas as pd
from django.db.models import Q, Count
import io
from .models import StudentData, ImportLog, TransferRecord
from .serializers import StudentDataSerializer, ImportLogSerializer, TransferRecordSerializer, TransferInSerializer, TransferOutSerializer
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import calendar
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from .crypto import decrypt_password, is_encrypted_request

from .models import Subject, Exam, Grade
from .serializers import SubjectSerializer, ExamSerializer, GradeSerializer, GradeDetailSerializer
from .permissions import IsAdminUser, IsReadOnlyUser, admin_required, get_user_permissions

# CSRF Token获取端点
class CSRFTokenView(APIView):
    """获取CSRF Token"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """返回CSRF token给前端"""
        csrf_token = get_token(request)
        return Response({
            'csrfToken': csrf_token
        })

# 认证相关API视图 - 移除CSRF豁免
class LoginView(APIView):
    """用户登录API"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            
            # 检查是否是加密请求
            if is_encrypted_request(data):
                # 解密密码
                try:
                    password = decrypt_password(
                        data.get('encryptedPassword'),
                        data.get('iv'),
                        data.get('timestamp')
                    )
                    print(f"🔓 密码解密成功，用户: {username}")
                except ValueError as e:
                    return Response({
                        'error': str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # 兼容明文密码（用于调试）
                password = data.get('password')
                print(f"⚠️ 收到明文密码请求，用户: {username}")
            
            if not username or not password:
                return Response({
                    'error': '用户名和密码不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 验证用户
            user = authenticate(username=username, password=password)
            if user is None:
                return Response({
                    'error': '用户名或密码错误'
                }, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_active:
                return Response({
                    'error': '账户已被禁用'
                }, status=status.HTTP_401_UNAUTHORIZED)

            # 生成JWT token
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'message': '登录成功',
                'token': str(access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"登录过程中发生错误: {str(e)}")
            return Response({
                'error': '登录过程中发生错误，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    """用户登出API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                
            return Response({
                'message': '登出成功'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': '登出失败'
            }, status=status.HTTP_400_BAD_REQUEST)

# 在UserInfoView中添加权限信息
class UserInfoView(APIView):
    """获取用户信息API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        permissions = get_user_permissions(user)
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            },
            'permissions': permissions
        }, status=status.HTTP_200_OK)

class StudentDataImportView(APIView):
    """学生数据导入 - 仅管理员"""
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        if 'file' not in request.FILES:
            return Response(
                {'error': '请选择要上传的文件'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        filename = file.name
        
        # 检查文件类型
        if not filename.endswith(('.xlsx', '.xls', '.csv')):
            return Response(
                {'error': '只支持Excel(.xlsx, .xls)或CSV文件'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 读取文件
            if filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
            else:
                df = pd.read_excel(file)
            
            # 检查必要的列是否存在（只保留必填字段）
            required_columns = [
                '学号', '姓名', '身份证号', '年龄', '年级', '班级', '广州学籍号'
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response(
                    {'error': f'缺少必要的列: {", ".join(missing_columns)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 检查可选列是否存在，如果不存在则添加空列
            optional_columns = [
                '全国学籍号', '户籍所在地', '居住所在地', 
                '监护人(父亲)', '监护人(母亲)', 
                '监护人(父亲)电话', '监护人(母亲)电话'
            ]
            
            for col in optional_columns:
                if col not in df.columns:
                    df[col] = None
            
            # 处理数据导入
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # 构建查询条件，排除空值字段
                    query_conditions = Q(school_id=str(row['学号'])) | Q(id_card=str(row['身份证号']))
                    
                    # 只有当广州学籍号不为空时才检查重复
                    if pd.notna(row['广州学籍号']) and str(row['广州学籍号']).strip():
                        query_conditions |= Q(gz_student_id=str(row['广州学籍号']))
                    
                    # 只有当全国学籍号不为空时才检查重复
                    if pd.notna(row['全国学籍号']) and str(row['全国学籍号']).strip():
                        query_conditions |= Q(national_student_id=str(row['全国学籍号']))
                    
                    existing = StudentData.objects.filter(query_conditions).first()
                    
                    if existing:
                        error_count += 1
                        errors.append(f'第{index+2}行: 学号、身份证号或学籍号已存在')
                        continue
                    
                    # 安全地处理可能为空的字段
                    def safe_get_value(row, column_name):
                        """安全获取列值，处理空值情况"""
                        if column_name not in row.index:
                            return None
                        value = row[column_name]
                        if pd.isna(value) or str(value).strip() == '' or str(value).lower() == 'nan':
                            return None
                        return str(value).strip()
                    
                    # 处理各个字段
                    national_student_id_value = safe_get_value(row, '全国学籍号')
                    grade_value = safe_get_value(row, '年级')
                    class_name_value = safe_get_value(row, '班级')
                    household_address_value = safe_get_value(row, '户籍所在地')
                    living_address_value = safe_get_value(row, '居住所在地')
                    guardian_father_value = safe_get_value(row, '监护人(父亲)')
                    guardian_mother_value = safe_get_value(row, '监护人(母亲)')
                    guardian_father_phone_value = safe_get_value(row, '监护人(父亲)电话')
                    guardian_mother_phone_value = safe_get_value(row, '监护人(母亲)电话')
                    
                    # 验证必填字段
                    if not str(row['学号']).strip():
                        error_count += 1
                        errors.append(f'第{index+2}行: 学号不能为空')
                        continue
                    
                    if not str(row['姓名']).strip():
                        error_count += 1
                        errors.append(f'第{index+2}行: 姓名不能为空')
                        continue
                    
                    if not str(row['广州学籍号']).strip():
                        error_count += 1
                        errors.append(f'第{index+2}行: 广州学籍号不能为空')
                        continue
                    
                    StudentData.objects.create(
                        school_id=str(row['学号']).strip(),
                        name=str(row['姓名']).strip(),
                        id_card=str(row['身份证号']).strip(),
                        age=int(row['年龄']),
                        grade=grade_value,
                        class_name=class_name_value,
                        gz_student_id=str(row['广州学籍号']).strip(),
                        national_student_id=national_student_id_value,
                        household_address=household_address_value,
                        living_address=living_address_value,
                        guardian_father=guardian_father_value,
                        guardian_mother=guardian_mother_value,
                        guardian_father_phone=guardian_father_phone_value,
                        guardian_mother_phone=guardian_mother_phone_value
                    )
                    success_count += 1
                except ValueError as ve:
                    error_count += 1
                    errors.append(f'第{index+2}行: 数据格式错误 - {str(ve)}')
                except Exception as e:
                    error_count += 1
                    errors.append(f'第{index+2}行: {str(e)}')
            
            # 创建导入日志
            import_log = ImportLog.objects.create(
                filename=filename,
                total_records=len(df),
                success_records=success_count,
                error_records=error_count,
                errors='\n'.join(errors)
            )
            
            return Response({
                'message': '导入完成',
                'total_records': len(df),
                'success_records': success_count,
                'error_records': error_count,
                'errors': errors[:10] if errors else []  # 只返回前10个错误
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'处理文件时出错: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StudentDataListView(APIView):
    """学生数据列表视图 - 所有用户可查看"""
    permission_classes = [IsReadOnlyUser]
    
    def get(self, request):
        try:
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            search = request.GET.get('search', '')
            
            # **重要：只查询在校学生，过滤掉已转出的学生**
            queryset = StudentData.objects.filter(status='active')
            
            # 搜索功能
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(school_id__icontains=search) |
                    Q(id_card__icontains=search)
                )
            
            # 排序
            queryset = queryset.order_by('-created_at')
            
            # 分页处理
            if page_size == 999999:  # 显示全部
                students = queryset
                total = queryset.count()
            else:
                paginator = Paginator(queryset, page_size)
                students = paginator.get_page(page)
                total = paginator.count
            
            # 序列化数据
            serializer = StudentDataSerializer(students, many=True)
            
            return Response({
                'data': serializer.data,
                'total': total,
                'page': page,
                'page_size': page_size,
                'has_next': hasattr(students, 'has_next') and students.has_next(),
                'has_previous': hasattr(students, 'has_previous') and students.has_previous()
            })
            
        except Exception as e:
            return Response(
                {'error': f'获取学生数据失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ImportLogView(APIView):
    """获取导入日志"""
    def get(self, request):
        logs = ImportLog.objects.all()[:20]  # 最近20条记录
        serializer = ImportLogSerializer(logs, many=True)
        return Response(serializer.data)

class StudentDataDeleteView(APIView):
    """学生数据删除 - 仅管理员"""
    permission_classes = [IsAdminUser]
    
    def delete(self, request):
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response(
                {'error': '请选择要删除的数据'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 检查要删除的数据是否存在
            existing_count = StudentData.objects.filter(id__in=ids).count()
            if existing_count != len(ids):
                return Response(
                    {'error': '部分数据不存在'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 执行删除
            deleted_count, _ = StudentData.objects.filter(id__in=ids).delete()
            
            return Response({
                'message': f'成功删除 {deleted_count} 条数据',
                'deleted_count': deleted_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'删除失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StudentDataUpdateView(APIView):
    """学生数据更新 - 仅管理员"""
    permission_classes = [IsAdminUser]
    
    def put(self, request, student_id):
        try:
            student = StudentData.objects.get(id=student_id)
        except StudentData.DoesNotExist:
            return Response(
                {'error': '学生数据不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # 检查唯一性约束（排除当前记录）
            school_id = request.data.get('school_id')
            id_card = request.data.get('id_card')
            gz_student_id = request.data.get('gz_student_id')
            
            # 检查学号是否被其他记录使用
            if school_id and StudentData.objects.exclude(id=student_id).filter(school_id=school_id).exists():
                return Response(
                    {'error': '学号已被其他学生使用'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 检查身份证号是否被其他记录使用
            if id_card and StudentData.objects.exclude(id=student_id).filter(id_card=id_card).exists():
                return Response(
                    {'error': '身份证号已被其他学生使用'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 检查广州学籍号是否被其他记录使用
            if gz_student_id and StudentData.objects.exclude(id=student_id).filter(gz_student_id=gz_student_id).exists():
                return Response(
                    {'error': '广州学籍号已被其他学生使用'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 更新数据
            serializer = StudentDataSerializer(student, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': '更新成功',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': '数据验证失败', 'details': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except Exception as e:
            return Response(
                {'error': f'更新失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StudentDataDetailView(APIView):
    """获取单个学生详细信息"""
    def get(self, request, student_id):
        try:
            student = StudentData.objects.get(id=student_id)
            serializer = StudentDataSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StudentData.DoesNotExist:
            return Response(
                {'error': '学生数据不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class TransferInView(APIView):
    """学生转入处理 - 仅管理员"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        print(f"收到转入请求数据: {request.data}")
        
        serializer = TransferInSerializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"数据验证失败: {serializer.errors}")
            return Response(
                {'error': '数据验证失败', 'details': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            data = serializer.validated_data
            print(f"验证后的数据: {data}")
            
            # 检查学号和身份证号是否已存在
            if StudentData.objects.filter(school_id=data['school_id']).exists():
                return Response(
                    {'error': f"学号 {data['school_id']} 已存在"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if StudentData.objects.filter(id_card=data['id_card']).exists():
                return Response(
                    {'error': f"身份证号 {data['id_card']} 已存在"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if StudentData.objects.filter(gz_student_id=data['gz_student_id']).exists():
                return Response(
                    {'error': f"广州学籍号 {data['gz_student_id']} 已存在"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 如果提供了全国学籍号，检查是否重复
            if data.get('national_student_id'):
                if StudentData.objects.filter(national_student_id=data['national_student_id']).exists():
                    return Response(
                        {'error': f"全国学籍号 {data['national_student_id']} 已存在"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # 创建学生数据
            student_data = {
                'school_id': data['school_id'],
                'name': data['name'],
                'id_card': data['id_card'],
                'age': data['age'],
                'grade': data['grade'],
                'class_name': data['class_name'],
                'gz_student_id': data['gz_student_id'],
                'national_student_id': data.get('national_student_id') or None,
                'household_address': data.get('household_address') or None,
                'living_address': data.get('living_address') or None,
                'guardian_father': data.get('guardian_father') or None,
                'guardian_mother': data.get('guardian_mother') or None,
                'guardian_father_phone': data.get('guardian_father_phone') or None,
                'guardian_mother_phone': data.get('guardian_mother_phone') or None,
            }
            
            print(f"准备创建学生数据: {student_data}")
            student = StudentData.objects.create(**student_data)
            print(f"学生数据创建成功: {student.id}")
            
            # 创建转学记录
            transfer_record_data = {
                'student': student,
                'transfer_type': 'transfer_in',
                'transfer_date': data['transfer_date'],
                'transfer_reason': data['transfer_reason'],
                'previous_school': data.get('previous_school') or None,
                'target_school': '本校',  # 转入时目标学校就是本校
                'transfer_grade': data['grade'],
                'transfer_class': data['class_name'],
                'status': 'completed',  # 转入完成
                'processor': '系统自动',
                'process_time': timezone.now(),
                'remarks': f"学生 {data['name']} 成功转入 {data['grade']}{data['class_name']}"
            }
            
            print(f"准备创建转学记录: {transfer_record_data}")
            transfer_record = TransferRecord.objects.create(**transfer_record_data)
            print(f"转学记录创建成功: {transfer_record.id}")
            
            return Response({
                'message': '学生转入成功',
                'student_id': student.id,
                'transfer_record_id': transfer_record.id,
                'data': {
                    'name': student.name,
                    'school_id': student.school_id,
                    'grade': student.grade,
                    'class_name': student.class_name
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"转入处理异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'转入处理失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TransferRecordListView(APIView):
    """获取转学记录列表"""
    def get(self, request):
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        search = request.GET.get('search', '')
        transfer_type = request.GET.get('transfer_type', '')
        
        queryset = TransferRecord.objects.all()
        
        # 搜索功能
        if search:
            queryset = queryset.filter(
                Q(student__name__icontains=search) |
                Q(student__school_id__icontains=search) |
                Q(transfer_reason__icontains=search)
            )
        
        # 按转学类型筛选
        if transfer_type:
            queryset = queryset.filter(transfer_type=transfer_type)
        
        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        data = queryset[start:end]
        
        serializer = TransferRecordSerializer(data, many=True)
        
        return Response({
            'data': serializer.data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })

class TransferRecordDetailView(APIView):
    """获取转学记录详情"""
    def get(self, request, record_id):
        try:
            record = TransferRecord.objects.get(id=record_id)
            serializer = TransferRecordSerializer(record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TransferRecord.DoesNotExist:
            return Response(
                {'error': '转学记录不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class TransferOutView(APIView):
    """学生转出处理 - 仅管理员"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        print(f"收到转出请求数据: {request.data}")
        
        serializer = TransferOutSerializer(data=request.data)
        
        if not serializer.is_valid():
            print(f"数据验证失败: {serializer.errors}")
            return Response(
                {'error': '数据验证失败', 'details': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            data = serializer.validated_data
            student_id = data['student_id']
            
            # 获取学生信息
            try:
                student = StudentData.objects.get(id=student_id, status='active')
            except StudentData.DoesNotExist:
                return Response(
                    {'error': '学生不存在或已转出'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # **修复：创建转出记录时正确设置状态和处理时间**
            transfer_record = TransferRecord.objects.create(
                student=student,
                transfer_type='transfer_out',
                target_school=data['target_school'],
                transfer_date=data['transfer_date'],
                target_grade=data.get('target_grade'),
                target_class=data.get('target_class'),
                transfer_reason=data['transfer_reason'],
                target_school_contact=data.get('target_school_contact'),
                target_school_phone=data.get('target_school_phone'),
                target_school_address=data.get('target_school_address'),
                processor=data.get('processor', '系统管理员'),  # 提供默认值
                approval_notes=data.get('approval_notes'),
                remarks=data.get('remarks'),
                # **关键修复：设置状态为已完成，设置处理时间**
                status='completed',  # 转出完成
                process_time=timezone.now()  # 设置处理时间为当前时间
            )
            
            # 更新学生状态为已转出
            student.status = 'transferred_out'
            student.save()
            
            print(f"转出记录创建成功: ID={transfer_record.id}, 状态={transfer_record.status}, 处理时间={transfer_record.process_time}")
            
            return Response({
                'message': '学生转出办理成功！',
                'transfer_record_id': transfer_record.id,
                'student_name': student.name,
                'target_school': data['target_school'],
                'status': transfer_record.status,
                'process_time': transfer_record.process_time.isoformat() if transfer_record.process_time else None
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"转出处理异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'转出处理失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TransferRecordUpdateView(APIView):
    """更新转学记录"""
    def put(self, request, record_id):
        try:
            # 获取转学记录
            try:
                record = TransferRecord.objects.get(id=record_id)
            except TransferRecord.DoesNotExist:
                return Response(
                    {'error': '转学记录不存在'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 获取更新数据
            new_status = request.data.get('status')
            processor = request.data.get('processor')
            approval_notes = request.data.get('approval_notes')
            remarks = request.data.get('remarks')
            
            # 验证状态值（删除approved）
            valid_statuses = ['pending', 'rejected', 'completed']
            if new_status and new_status not in valid_statuses:
                return Response(
                    {'error': f'无效的状态值。有效值为: {", ".join(valid_statuses)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 更新记录
            if new_status:
                record.status = new_status
                # 如果状态改为非待处理，设置处理时间
                if new_status != 'pending':
                    record.process_time = timezone.now()
                else:
                    record.process_time = None
            
            if processor:
                record.processor = processor
            
            if approval_notes is not None:
                record.approval_notes = approval_notes
                
            if remarks is not None:
                record.remarks = remarks
            
            record.updated_at = timezone.now()
            record.save()
            
            # 返回更新后的数据
            serializer = TransferRecordSerializer(record)
            
            return Response({
                'message': '转学记录更新成功',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'更新失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DashboardStatsView(APIView):
    """仪表盘统计数据视图"""
    
    def get(self, request):
        try:
            period = request.GET.get('period', 'month')
            
            # 基本统计
            total_students = StudentData.objects.filter(status='active').count()
            
            # 本月新增学生数（根据创建时间）
            now = timezone.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_students_this_month = StudentData.objects.filter(
                created_at__gte=month_start,
                status='active'
            ).count()
            
            # 转学相关统计
            transfer_in_count = TransferRecord.objects.filter(
                transfer_type='transfer_in',
                status='completed'
            ).count()
            
            transfer_out_count = TransferRecord.objects.filter(
                transfer_type='transfer_out', 
                status='completed'
            ).count()
            
            # 新增：休学和复学统计
            suspend_count = TransferRecord.objects.filter(
                transfer_type='suspend',
                status='completed'
            ).exclude(
                student__transfer_records__transfer_type='resume',
                student__transfer_records__status='completed'
            ).count()
            
            resume_count = TransferRecord.objects.filter(
                transfer_type='resume',
                status='completed'
            ).count()
            
            # 待处理的异动申请
            pending_transfers = TransferRecord.objects.filter(
                status='pending'
            ).count()
            
            # 年级分布统计
            grade_stats = []
            total_active_students = StudentData.objects.filter(status='active').count()
            
            if total_active_students > 0:
                grades = StudentData.objects.filter(status='active').values('grade').annotate(
                    count=Count('id')
                ).order_by('grade')
                
                for grade_info in grades:
                    if grade_info['grade']:
                        percentage = round((grade_info['count'] / total_active_students) * 100, 1)
                        grade_stats.append({
                            'name': grade_info['grade'],
                            'count': grade_info['count'],
                            'percentage': percentage
                        })
            
            # 最近活动（最近的异动记录）
            recent_activities = []
            recent_transfers = TransferRecord.objects.select_related('student').order_by('-created_at')[:5]
            
            for transfer in recent_transfers:
                activity_type = transfer.transfer_type
                
                # 根据异动类型设置活动信息
                if transfer.transfer_type == 'transfer_in':
                    title = '学生转入'
                    description = f'{transfer.student.name}同学从{transfer.previous_school or "其他学校"}转入我校{transfer.transfer_grade or ""}{transfer.transfer_class or ""}'
                elif transfer.transfer_type == 'transfer_out':
                    title = '学生转出'
                    description = f'{transfer.student.name}同学转出到{transfer.target_school or "其他学校"}'
                elif transfer.transfer_type == 'suspend':
                    title = '学生休学'
                    description = f'{transfer.student.name}同学申请休学，原因：{transfer.transfer_reason[:20]}...' if len(transfer.transfer_reason) > 20 else f'{transfer.student.name}同学申请休学，原因：{transfer.transfer_reason}'
                elif transfer.transfer_type == 'resume':
                    title = '学生复学'
                    description = f'{transfer.student.name}同学申请复学到{transfer.transfer_grade or ""}{transfer.transfer_class or ""}'
                else:
                    title = '异动申请'
                    description = f'{transfer.student.name}同学申请{transfer.get_transfer_type_display()}'
                
                recent_activities.append({
                    'id': transfer.id,
                    'type': activity_type,
                    'title': title,
                    'description': description,
                    'time': transfer.created_at.isoformat()
                })
            
            # 简化的趋势数据
            trend_data = self.get_simple_trend_data()
            
            return Response({
                'statistics': {
                    'totalStudents': total_students,
                    'newStudentsThisMonth': new_students_this_month,
                    'transferInCount': transfer_in_count,
                    'transferOutCount': transfer_out_count,
                    'suspendCount': suspend_count,      # 新增
                    'resumeCount': resume_count,        # 新增
                    'pendingTransfers': pending_transfers
                },
                'gradeDistribution': grade_stats,
                'recentActivities': recent_activities,
                'trendData': trend_data
            })
            
        except Exception as e:
            print(f"获取仪表盘数据失败: {str(e)}")
            return Response({
                'error': f'获取数据失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_simple_trend_data(self):
        """获取简化的趋势数据"""
        try:
            # 获取最近12个月的数据
            months = []
            transfer_in_data = []
            transfer_out_data = []
            student_count_data = []
            
            current_students = StudentData.objects.filter(status='active').count()
            
            # 生成最近12个月的标签
            now = timezone.now()
            for i in range(11, -1, -1):  # 从11个月前到现在
                month_date = now - timedelta(days=30 * i)
                month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                month_end = (month_start.replace(month=month_start.month % 12 + 1, day=1) if month_start.month != 12 
                           else month_start.replace(year=month_start.year + 1, month=1, day=1))
                
                months.append(month_date.strftime('%Y-%m'))
                
                # 统计该月的实际转入转出数据
                month_transfer_in = TransferRecord.objects.filter(
                    transfer_type='transfer_in',
                    created_at__gte=month_start,
                    created_at__lt=month_end
                ).count()
                
                month_transfer_out = TransferRecord.objects.filter(
                    transfer_type='transfer_out',
                    created_at__gte=month_start,
                    created_at__lt=month_end
                ).count()
                
                transfer_in_data.append(month_transfer_in)
                transfer_out_data.append(month_transfer_out)
                student_count_data.append(current_students)
            
            return {
                'period': 'month',
                'dates': months,
                'transferIn': transfer_in_data,
                'transferOut': transfer_out_data,
                'studentCount': student_count_data,
                'currentDateIndex': 11  # 当前月份在数组中的位置（最后一个）
            }
            
        except Exception as e:
            print(f"get_simple_trend_data错误: {str(e)}")
            # 返回默认数据
            return {
                'period': 'month',
                'dates': ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06'],
                'transferIn': [5, 3, 8, 2, 6, 4],
                'transferOut': [2, 1, 3, 1, 2, 1],
                'studentCount': [1000, 1003, 1008, 1009, 1013, 1016],
                'currentDateIndex': 5
            }

class StudentSuspendView(APIView):
    """学生休学处理"""
    
    def post(self, request):
        try:
            data = request.data
            print(f"收到休学请求数据: {data}")
            
            # 验证学生存在
            try:
                student = StudentData.objects.get(id=data['student_id'])
            except StudentData.DoesNotExist:
                return Response({
                    'error': '学生不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 检查是否已经休学
            current_status = student.get_current_status()
            if current_status == 'suspended':
                return Response({
                    'error': '该学生已经在休学状态'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建休学记录
            transfer_record = TransferRecord.objects.create(
                student=student,
                transfer_type='suspend',
                transfer_date=data['suspend_start_date'],
                transfer_reason=data['transfer_reason'],
                expected_resume_date=data.get('expected_resume_date'),
                contact_person=data.get('contact_person'),
                contact_phone=data.get('contact_phone'),
                status='completed',
                processor=data.get('processor', '系统管理员'),
                process_time=timezone.now(),
                remarks=data.get('remarks', f"学生 {student.name} 申请休学")
            )
            
            # 不需要直接修改学生状态，通过get_current_status()方法动态判断
            
            return Response({
                'message': '休学申请提交成功',
                'record_id': transfer_record.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"休学申请失败: {str(e)}")
            return Response({
                'error': f'休学申请失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentResumeView(APIView):
    """学生复学处理"""
    
    def post(self, request):
        try:
            data = request.data
            print(f"收到复学请求数据: {data}")
            
            # 验证学生存在
            try:
                student = StudentData.objects.get(id=data['student_id'])
            except StudentData.DoesNotExist:
                return Response({
                    'error': '学生不存在'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 检查是否在休学状态
            current_status = student.get_current_status()
            if current_status != 'suspended':
                return Response({
                    'error': '该学生不在休学状态，无法复学'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建复学记录
            transfer_record = TransferRecord.objects.create(
                student=student,
                transfer_type='resume',
                transfer_date=data['resume_date'],
                transfer_reason=data['transfer_reason'],
                transfer_grade=data['resume_grade'],
                transfer_class=data['resume_class'],
                status='completed',
                processor=data.get('processor', '系统管理员'),
                process_time=timezone.now(),
                approval_notes=data.get('approval_notes'),
                remarks=data.get('remarks', f"学生 {student.name} 申请复学到 {data['resume_grade']}{data['resume_class']}")
            )
            
            # 更新学生年级班级信息
            student.grade = data['resume_grade']
            student.class_name = data['resume_class']
            student.save()
            
            return Response({
                'message': '复学申请提交成功',
                'record_id': transfer_record.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"复学申请失败: {str(e)}")
            return Response({
                'error': f'复学申请失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SuspendedStudentsView(APIView):
    """获取休学学生列表"""
    
    def get(self, request):
        try:
            # 获取当前休学状态的学生
            suspended_students = TransferRecord.objects.filter(
                transfer_type='suspend',
                status='completed'
            ).exclude(
                student__transfer_records__transfer_type='resume',
                student__transfer_records__status='completed'
            ).select_related('student')
            
            data = []
            for record in suspended_students:
                student = record.student
                data.append({
                    'id': student.id,
                    'name': student.name,
                    'school_id': student.school_id,
                    'grade': student.grade,
                    'class_name': student.class_name,
                    'suspend_date': record.transfer_date,
                    'suspend_reason': record.transfer_reason,
                    'expected_resume_date': record.expected_resume_date
                })
            
            return Response({
                'data': data,
                'total': len(data)
            })
            
        except Exception as e:
            return Response({
                'error': f'获取休学学生列表失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def health_check(request):
    """健康检查端点"""
    try:
        # 检查数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'message': 'Service is running'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }, status=500)

class SubjectListView(APIView):
    """科目列表API"""
    def get(self, request):
        subjects = Subject.objects.filter(is_active=True)
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExamListView(APIView):
    """考试列表API"""
    def get(self, request):
        try:
            # 只处理有效的过滤参数
            academic_year = request.GET.get('academic_year')
            semester = request.GET.get('semester')
            
            queryset = Exam.objects.all().order_by('-exam_date')
            
            # 只有当参数存在且不为空时才过滤
            if academic_year:
                queryset = queryset.filter(academic_year=academic_year)
            if semester:
                queryset = queryset.filter(semester=semester)
                
            serializer = ExamSerializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            print(f"获取考试列表失败: {str(e)}")
            return Response({'error': f'获取考试列表失败: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        serializer = ExamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GradeListView(APIView):
    """成绩列表API"""
    def get(self, request):
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        student_id = request.GET.get('student_id')
        exam_id = request.GET.get('exam_id')
        subject_id = request.GET.get('subject_id')
        grade_filter = request.GET.get('grade')
        class_filter = request.GET.get('class')
        
        queryset = Grade.objects.select_related('student', 'subject', 'exam')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if grade_filter:
            queryset = queryset.filter(student__grade=grade_filter)
        if class_filter:
            queryset = queryset.filter(student__class_name=class_filter)
            
        paginator = Paginator(queryset, page_size)
        grades = paginator.get_page(page)
        
        serializer = GradeSerializer(grades, many=True)
        return Response({
            'data': serializer.data,
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'has_next': grades.has_next(),
            'has_previous': grades.has_previous()
        })

class GradeCreateView(APIView):
    """创建成绩记录"""
    def post(self, request):
        serializer = GradeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GradeAnalysisView(APIView):
    """成绩分析API"""
    def get(self, request):
        exam_id = request.GET.get('exam_id')
        grade_filter = request.GET.get('grade')
        class_filter = request.GET.get('class')
        
        if not exam_id:
            return Response({'error': '请选择考试'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Grade.objects.filter(exam_id=exam_id)
        
        if grade_filter:
            queryset = queryset.filter(student__grade=grade_filter)
        if class_filter:
            queryset = queryset.filter(student__class_name=class_filter)
        
        from django.db.models import Avg, Max, Min, Count
        
        analysis_data = {}
        
        subjects = queryset.values('subject__name').annotate(
            avg_score=Avg('score'),
            max_score=Max('score'),
            min_score=Min('score'),
            student_count=Count('student')
        )
        
        analysis_data['subject_stats'] = list(subjects)
        
        score_ranges = [
            (90, 100, 'A'),
            (80, 89, 'B'),
            (70, 79, 'C'),
            (60, 69, 'D'),
            (0, 59, 'F')
        ]
        
        score_distribution = []
        for min_score, max_score, level in score_ranges:
            count = queryset.filter(score__gte=min_score, score__lte=max_score).count()
            score_distribution.append({
                'level': level,
                'range': f'{min_score}-{max_score}',
                'count': count
            })
        
        analysis_data['score_distribution'] = score_distribution
        
        return Response(analysis_data)

class GradeMatrixView(APIView):
    """横向成绩查询API - 学生成绩矩阵"""
    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            exam_id = request.GET.get('exam_id')
            grade_filter = request.GET.get('grade')
            class_filter = request.GET.get('class')
            
            if not exam_id:
                return Response({'error': '请选择考试'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取该考试的所有科目
            subject_ids = Grade.objects.filter(exam_id=exam_id).values_list('subject_id', flat=True).distinct()
            subjects = Subject.objects.filter(id__in=subject_ids, is_active=True).order_by('name')
            
            # 获取该考试下的所有学生成绩
            grades_queryset = Grade.objects.filter(exam_id=exam_id).select_related('student', 'subject')
            
            # 应用过滤条件
            if grade_filter:
                grades_queryset = grades_queryset.filter(student__grade=grade_filter)
            if class_filter:
                grades_queryset = grades_queryset.filter(student__class_name__icontains=class_filter)
            
            # 获取所有相关学生
            student_ids = grades_queryset.values_list('student_id', flat=True).distinct()
            students = StudentData.objects.filter(id__in=student_ids).order_by('school_id')
            
            # 分页处理
            paginator = Paginator(students, page_size)
            try:
                page_students = paginator.page(page)
            except:
                page_students = paginator.page(1)
            
            # 构建成绩矩阵数据
            result_data = []
            
            # 获取当前页学生的所有成绩
            page_student_ids = [s.id for s in page_students]
            grades_data = Grade.objects.filter(
                exam_id=exam_id,
                student_id__in=page_student_ids
            ).select_related('subject')
            
            # 按学生分组成绩数据
            student_grades = {}
            student_total_ranks = {}  # 🆕 存储总分排名
            
            for grade in grades_data:
                if grade.student_id not in student_grades:
                    student_grades[grade.student_id] = {}
                    student_total_ranks[grade.student_id] = {
                        'total_rank_in_grade': grade.total_rank_in_grade,
                        'total_rank_in_class': grade.total_rank_in_class
                    }
                
                student_grades[grade.student_id][grade.subject.code] = {
                    'score': float(grade.score),
                    'rank_in_class': grade.rank_in_class,
                    'rank_in_grade': grade.rank_in_grade
                }
            
            # 构建最终数据结构
            for student in page_students:
                student_data = {
                    'id': student.id,
                    'school_id': student.school_id,
                    'name': student.name,
                    'grade': student.grade,
                    'class_name': student.class_name,
                    'subjects': student_grades.get(student.id, {}),
                    'total_score': 0,
                    'total_rank_in_grade': None,
                    'total_rank_in_class': None
                }
                
                # 计算总分
                if student.id in student_grades:
                    total_score = sum(
                        subj_data['score'] 
                        for subj_data in student_grades[student.id].values()
                    )
                    student_data['total_score'] = total_score
                    
                    # 🆕 获取总分排名
                    if student.id in student_total_ranks:
                        student_data['total_rank_in_grade'] = student_total_ranks[student.id]['total_rank_in_grade']
                        student_data['total_rank_in_class'] = student_total_ranks[student.id]['total_rank_in_class']
                
                result_data.append(student_data)
            
            # 准备科目列表数据
            subjects_data = [
                {
                    'id': subject.id,
                    'name': subject.name,
                    'code': subject.code,
                    'category': subject.category
                }
                for subject in subjects
            ]
            
            return Response({
                'data': result_data,
                'subjects': subjects_data,
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages
            })
            
        except Exception as e:
            print(f"获取成绩矩阵失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'获取成绩矩阵失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GradeMatrixExportView(APIView):
    """导出横向成绩数据"""
    def get(self, request):
        try:
            import pandas as pd
            from django.http import HttpResponse
            import io
            
            exam_id = request.GET.get('exam_id')
            grade_filter = request.GET.get('grade')
            class_filter = request.GET.get('class')
            
            if not exam_id:
                return Response({'error': '请选择考试'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取该考试的所有科目
            subjects = Subject.objects.filter(
                grades__exam_id=exam_id,
                is_active=True
            ).distinct().order_by('name')
            
            # 获取学生列表
            student_query = StudentData.objects.filter(
                grades__exam_id=exam_id
            ).distinct()
            
            if grade_filter:
                student_query = student_query.filter(grade=grade_filter)
            if class_filter:
                student_query = student_query.filter(class_name=class_filter)
            
            if not student_query.exists():
                return Response({'error': '没有找到符合条件的成绩数据'}, 
                              status=status.HTTP_404_NOT_FOUND)
            
            # 构建导出数据
            export_data = []
            for student in student_query:
                row_data = {
                    '学号': student.school_id,
                    '姓名': student.name,
                    '年级': student.grade or '',
                    '班级': student.class_name or '',
                }
                
                # 获取该学生的所有成绩
                grades = Grade.objects.filter(
                    student=student,
                    exam_id=exam_id
                ).select_related('subject')
                
                total_score = 0
                subject_count = 0
                
                # 添加各科目成绩和排名
                for subject in subjects:
                    grade = grades.filter(subject=subject).first()
                    if grade:
                        row_data[subject.name] = float(grade.score)
                        row_data[f'{subject.name}排名'] = grade.rank_in_class or ''
                        total_score += float(grade.score)
                        subject_count += 1
                    else:
                        row_data[subject.name] = ''
                        row_data[f'{subject.name}排名'] = ''
                
                # 添加总分
                row_data['总分'] = total_score if subject_count > 0 else ''
                row_data['总分排名'] = ''  # 这里可以后续计算
                
                export_data.append(row_data)
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 创建Excel文件
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='成绩单', index=False)
                
                # 设置列宽
                worksheet = writer.sheets['成绩单']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 15)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            
            # 设置响应
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            from datetime import datetime
            filename = f'成绩单_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            return Response({'error': f'导出失败: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GradeMatrixTemplateView(APIView):
    """下载横向成绩导入模板"""
    def get(self, request):
        try:
            import pandas as pd
            from django.http import HttpResponse
            import io
            
            # 获取所有活跃科目
            subjects = Subject.objects.filter(is_active=True).order_by('name')
            
            # 构建模板列头
            columns = ['学号', '姓名', '年级', '班级']
            
            # 添加各科目列
            for subject in subjects:
                columns.extend([subject.name, f'{subject.name}排名'])
            
            # 添加总分列
            columns.extend(['总分', '总分排名'])
            
            # 创建示例数据
            sample_data = []
            sample_students = [
                {'学号': '20240001', '姓名': '张三', '年级': '七年级', '班级': '1班'},
                {'学号': '20240002', '姓名': '李四', '年级': '七年级', '班级': '1班'},
                {'学号': '20240003', '姓名': '王五', '年级': '七年级', '班级': '2班'},
            ]
            
            for student in sample_students:
                row = student.copy()
                total_score = 0
                
                # 为每个科目填入示例分数
                for i, subject in enumerate(subjects):
                    score = 85 + (i * 3) + (hash(student['学号']) % 10)
                    row[subject.name] = score
                    row[f'{subject.name}排名'] = (i % 5) + 1
                    total_score += score
                
                row['总分'] = total_score
                row['总分排名'] = hash(student['学号']) % 20 + 1
                
                sample_data.append(row)
            
            # 创建DataFrame
            df = pd.DataFrame(sample_data, columns=columns)
            
            # 创建说明数据
            instructions_data = {
                '字段说明': [
                    '学号：学生学号，必填，必须在系统中存在',
                    '姓名：学生姓名，选填，用于核对',
                    '年级：学生年级，选填，用于核对',
                    '班级：学生班级，选填，用于核对',
                    '科目成绩：各科目分数，数字格式',
                    '科目排名：各科目排名，数字格式，选填',
                    '总分：所有科目总分，可自动计算',
                    '总分排名：总分排名，数字格式，选填'
                ],
                '注意事项': [
                    '学号列是必填项，其他可以留空',
                    '成绩列请填入数字，支持小数',
                    '排名列选填，不填时系统会自动计算',
                    '请不要修改表头格式',
                    '导入前请确保学生已在系统中',
                    '导入前请确保科目已在系统中设置',
                    '建议先小批量测试导入',
                    '有问题请联系系统管理员'
                ]
            }
            instructions_df = pd.DataFrame(instructions_data)
            
            # 科目列表
            subjects_data = {
                '科目名称': [subject.name for subject in subjects],
                '科目代码': [subject.code for subject in subjects],
                '科目类别': [subject.get_category_display() for subject in subjects]
            }
            subjects_df = pd.DataFrame(subjects_data)
            
            # 创建Excel文件
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # 写入模板数据
                df.to_excel(writer, sheet_name='成绩模板', index=False)
                
                # 写入说明
                instructions_df.to_excel(writer, sheet_name='导入说明', index=False)
                
                # 写入科目列表
                subjects_df.to_excel(writer, sheet_name='科目列表', index=False)
                
                # 设置列宽
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 20)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            
            # 设置响应
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            response['Content-Disposition'] = 'attachment; filename="横向成绩导入模板.xlsx"'
            
            return response
            
        except Exception as e:
            return Response({'error': f'生成模板失败: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GradeMatrixImportView(APIView):
    """成绩导入 - 仅管理员"""
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        print(f"收到横向成绩导入请求: {request.data}")
        
        if 'file' not in request.FILES:
            return Response({'error': '请选择要上传的文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        exam_id = request.data.get('exam_id')
        
        if not exam_id:
            return Response({'error': '请选择考试'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response({'error': f'考试ID {exam_id} 不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            import pandas as pd
            import io
            
            # 读取Excel文件
            if file.name.endswith('.csv'):
                df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
            else:
                df = pd.read_excel(file)
            
            print(f"读取到 {len(df)} 行数据")
            print(f"列名: {list(df.columns)}")
            
            # 检查必要列
            required_columns = ['学号']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response({'error': f'缺少必要的列: {", ".join(missing_columns)}'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # 获取科目列（排除基础信息列）
            basic_columns = ['学号', '姓名', '年级', '班级', '总分', '总分排名']
            subject_columns = []
            rank_columns = []
            
            for col in df.columns:
                if col not in basic_columns:
                    if col.endswith('排名'):
                        rank_columns.append(col)
                    else:
                        subject_columns.append(col)
            
            print(f"识别到科目列: {subject_columns}")
            print(f"识别到排名列: {rank_columns}")
            
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    school_id = str(row['学号']).strip()
                    print(f"处理第{index+1}行: 学号={school_id}")
                    
                    # 查找学生
                    try:
                        student = StudentData.objects.get(school_id=school_id)
                        print(f"找到学生: {student.name}")
                    except StudentData.DoesNotExist:
                        error_count += 1
                        errors.append(f'第{index+2}行: 学号 {school_id} 不存在')
                        continue
                    
                    # 🆕 获取总分排名数据
                    total_rank_in_grade = None
                    total_rank_in_class = None
                    
                    if '总分排名' in df.columns and not pd.isna(row['总分排名']):
                        try:
                            # 假设总分排名是年级排名，也可以根据需要调整
                            total_rank_in_grade = int(row['总分排名'])
                            print(f"总分排名: {total_rank_in_grade}")
                        except (ValueError, TypeError):
                            print(f"总分排名格式错误: {row['总分排名']}")
                    
                    # 处理每个科目的成绩
                    student_success = 0
                    created_grades = []  # 存储创建的成绩记录
                    
                    for subject_name in subject_columns:
                        try:
                            score_value = row[subject_name]
                            
                            # 跳过空值
                            if pd.isna(score_value) or score_value == '':
                                continue
                            
                            # 查找科目
                            try:
                                subject = Subject.objects.get(name=subject_name, is_active=True)
                            except Subject.DoesNotExist:
                                # 如果科目不存在，尝试创建
                                subject = Subject.objects.create(
                                    name=subject_name,
                                    code=f"SUB_{subject_name[:3].upper()}",
                                    category='main',
                                    is_active=True
                                )
                                print(f"创建新科目: {subject.name}")
                            
                            # 获取单科排名
                            rank_column = f"{subject_name}排名"
                            rank_value = None
                            if rank_column in df.columns and not pd.isna(row[rank_column]):
                                try:
                                    rank_value = int(row[rank_column])
                                except (ValueError, TypeError):
                                    pass
                            
                            # 🆕 准备成绩数据（包含总分排名）
                            grade_data = {
                                'score': float(score_value),
                                'rank_in_class': rank_value,
                                'rank_in_grade': None,
                                'total_rank_in_class': total_rank_in_class,
                                'total_rank_in_grade': total_rank_in_grade,
                                'remarks': None,
                            }
                            
                            # 创建或更新成绩记录
                            grade, created = Grade.objects.update_or_create(
                                student=student,
                                subject=subject,
                                exam=exam,
                                defaults=grade_data
                            )
                            
                            created_grades.append(grade)
                            action = "创建" if created else "更新"
                            print(f"成功{action}成绩记录: {student.name} - {subject.name} - {grade.score}分 - 总排名:{total_rank_in_grade}")
                            student_success += 1
                            
                        except ValueError as ve:
                            error_count += 1
                            error_msg = f'第{index+2}行科目"{subject_name}": 分数格式错误 - {str(ve)}'
                            errors.append(error_msg)
                            print(f"分数格式错误: {error_msg}")
                        except Exception as e:
                            error_count += 1
                            error_msg = f'第{index+2}行科目"{subject_name}": {str(e)}'
                            errors.append(error_msg)
                            print(f"处理错误: {error_msg}")
                    
                    if student_success > 0:
                        success_count += 1
                        print(f"学生 {student.name} 成功导入 {student_success} 科成绩，总分排名：{total_rank_in_grade}")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f'第{index+2}行: {str(e)}'
                    errors.append(error_msg)
                    print(f"行处理错误: {error_msg}")
            
            result = {
                'message': '横向导入完成',
                'total_records': len(df),
                'success_records': success_count,
                'error_records': error_count,
                'errors': errors[:10]
            }
            
            print(f"横向导入结果: {result}")
            return Response(result)
            
        except Exception as e:
            error_msg = f'处理文件时出错: {str(e)}'
            print(f"文件处理错误: {error_msg}")
            return Response({'error': error_msg}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 添加权限检查API
class UserPermissionsView(APIView):
    """获取用户权限API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        permissions = get_user_permissions(request.user)
        return Response(permissions)
