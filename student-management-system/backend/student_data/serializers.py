from rest_framework import serializers
from .models import StudentData, ImportLog, TransferRecord
from .models import Subject, Exam, Grade

class StudentDataSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_current_status_display', read_only=True)
    status_color = serializers.CharField(source='get_status_display_color', read_only=True)
    current_status = serializers.CharField(source='get_current_status', read_only=True)
    
    class Meta:
        model = StudentData
        fields = [
            'id', 'school_id', 'name', 'id_card', 'age',
            'grade', 'class_name',
            'gz_student_id', 'national_student_id', 
            'household_address', 'living_address',
            'guardian_father', 'guardian_mother', 
            'guardian_father_phone', 'guardian_mother_phone',
            'status', 'current_status', 'status_display', 'status_color',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_status', 'status_display', 'status_color']

class TransferRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_school_id = serializers.CharField(source='student.school_id', read_only=True)
    student_grade = serializers.CharField(source='student.grade', read_only=True)
    student_class_name = serializers.CharField(source='student.class_name', read_only=True)
    transfer_type_display = serializers.CharField(source='get_transfer_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TransferRecord
        fields = '__all__'

class TransferInSerializer(serializers.Serializer):
    """转入数据序列化器"""
    # 基本信息
    name = serializers.CharField(max_length=50)
    school_id = serializers.CharField(max_length=20)
    grade = serializers.CharField(max_length=10)
    class_name = serializers.CharField(max_length=20)
    id_card = serializers.CharField(max_length=18)
    age = serializers.IntegerField(min_value=6, max_value=18)
    gz_student_id = serializers.CharField(max_length=30)
    national_student_id = serializers.CharField(max_length=30, required=False, allow_blank=True)
    
    # 地址信息
    household_address = serializers.CharField(required=False, allow_blank=True)
    living_address = serializers.CharField(required=False, allow_blank=True)
    
    # 监护人信息
    guardian_father = serializers.CharField(max_length=50, required=False, allow_blank=True)
    guardian_mother = serializers.CharField(max_length=50, required=False, allow_blank=True)
    guardian_father_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    guardian_mother_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    # 转学信息
    transfer_date = serializers.DateField()
    transfer_reason = serializers.CharField(min_length=5)  # 至少5个字符
    previous_school = serializers.CharField(max_length=100, required=False, allow_blank=True)
    transfer_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_id_card(self, value):
        """验证身份证号格式"""
        import re
        if not re.match(r'^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$', value):
            raise serializers.ValidationError('身份证号格式不正确')
        return value
    
    def validate_transfer_reason(self, value):
        """验证转学原因"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError('转学原因至少需要5个字符')
        return value.strip()

class ImportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportLog
        fields = '__all__'

class TransferOutSerializer(serializers.Serializer):
    """转出数据序列化器"""
    # 学生ID（从URL获取或传递）
    student_id = serializers.IntegerField()
    
    # 转出信息
    target_school = serializers.CharField(max_length=100, help_text="目标学校名称")
    transfer_date = serializers.DateField(help_text="转出日期")
    transfer_reason = serializers.CharField(min_length=5, help_text="转出原因")
    
    # 目标学校信息
    target_grade = serializers.CharField(max_length=10, required=False, allow_blank=True, help_text="转入目标年级")
    target_class = serializers.CharField(max_length=20, required=False, allow_blank=True, help_text="转入目标班级")
    target_school_contact = serializers.CharField(max_length=50, required=False, allow_blank=True, help_text="目标学校联系人")
    target_school_phone = serializers.CharField(max_length=20, required=False, allow_blank=True, help_text="目标学校联系电话")
    target_school_address = serializers.CharField(max_length=200, required=False, allow_blank=True, help_text="目标学校地址")
    
    # 处理信息
    processor = serializers.CharField(max_length=50, default="系统管理员", help_text="处理人")
    approval_notes = serializers.CharField(required=False, allow_blank=True, help_text="审批意见")
    remarks = serializers.CharField(required=False, allow_blank=True, help_text="备注信息")
    
    def validate_transfer_reason(self, value):
        """验证转出原因"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError('转出原因至少需要5个字符')
        return value.strip()
    
    def validate_student_id(self, value):
        """验证学生是否存在且可以转出"""
        try:
            student = StudentData.objects.get(id=value)
            if student.status == 'transferred_out':
                raise serializers.ValidationError('该学生已经转出，无法重复办理')
            if student.status == 'graduated':
                raise serializers.ValidationError('该学生已毕业，无法办理转出')
            return value
        except StudentData.DoesNotExist:
            raise serializers.ValidationError('学生不存在')

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_school_id = serializers.CharField(source='student.school_id', read_only=True)
    student_grade = serializers.CharField(source='student.grade', read_only=True)
    student_class = serializers.CharField(source='student.class_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    grade_level = serializers.CharField(source='get_grade_level', read_only=True)
    
    class Meta:
        model = Grade
        fields = '__all__'

class GradeDetailSerializer(serializers.ModelSerializer):
    """详细的成绩序列化器，包含关联对象的完整信息"""
    student = StudentDataSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)
    grade_level = serializers.CharField(source='get_grade_level', read_only=True)
    
    class Meta:
        model = Grade
        fields = '__all__'