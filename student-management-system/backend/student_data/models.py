from django.db import models

# Create your models here.

from django.db import models

class StudentData(models.Model):
    """学生数据模型"""
    STATUS_CHOICES = [
        ('active', '在校'),
        ('transferred_out', '已转出'),
        ('graduated', '已毕业'),
        ('suspended', '休学'),
    ]
    
    school_id = models.CharField(max_length=20, unique=True, verbose_name="学号")
    name = models.CharField(max_length=50, verbose_name="姓名")
    id_card = models.CharField(max_length=18, unique=True, verbose_name="身份证号")
    age = models.IntegerField(verbose_name="年龄")
    
    # 新添加的字段
    grade = models.CharField(max_length=10, verbose_name="年级", blank=True, null=True)
    class_name = models.CharField(max_length=20, verbose_name="班级", blank=True, null=True)
    
    gz_student_id = models.CharField(max_length=30, unique=True, verbose_name="广州学籍号")
    national_student_id = models.CharField(max_length=30, verbose_name="全国学籍号", blank=True, null=True)
    household_address = models.TextField(verbose_name="户籍所在地", blank=True, null=True)
    living_address = models.TextField(verbose_name="居住所在地", blank=True, null=True)
    guardian_father = models.CharField(max_length=50, verbose_name="监护人(父亲)", blank=True, null=True)
    guardian_mother = models.CharField(max_length=50, verbose_name="监护人(母亲)", blank=True, null=True)
    guardian_father_phone = models.CharField(max_length=20, verbose_name="监护人(父亲)电话", blank=True, null=True)
    guardian_mother_phone = models.CharField(max_length=20, verbose_name="监护人(母亲)电话", blank=True, null=True)
    
    # 状态字段
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="学生状态")
    
    # 系统字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "学生数据"
        verbose_name_plural = "学生数据"
        db_table = "student_data"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.school_id} - {self.name}"
    
    def get_current_status(self):
        """获取学生当前实际状态"""
        # 如果已经是转出或毕业状态，直接返回
        if self.status in ['transferred_out', 'graduated']:
            return self.status
        
        # 检查是否有休学记录且未复学
        suspend_record = self.transfer_records.filter(
            transfer_type='suspend',
            status='completed'
        ).order_by('-created_at').first()
        
        if suspend_record:
            # 检查是否有复学记录
            resume_record = self.transfer_records.filter(
                transfer_type='resume',
                status='completed',
                created_at__gt=suspend_record.created_at
            ).first()
            
            if not resume_record:
                return 'suspended'  # 仍在休学状态
        
        # 默认返回在校状态
        return 'active'
    
    def get_status_display_color(self):
        """获取状态显示颜色"""
        current_status = self.get_current_status()
        status_colors = {
            'active': 'success',
            'transferred_out': 'warning', 
            'graduated': 'info',
            'suspended': 'danger'
        }
        return status_colors.get(current_status, 'info')
    
    def get_current_status_display(self):
        """获取当前状态的中文显示"""
        current_status = self.get_current_status()
        status_dict = dict(self.STATUS_CHOICES)
        return status_dict.get(current_status, '未知')

class TransferRecord(models.Model):
    """转学记录模型"""
    TRANSFER_TYPE_CHOICES = [
        ('transfer_in', '转入'),
        ('transfer_out', '转出'),
        ('suspend', '休学'),
        ('resume', '复学'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('completed', '已完成'),
    ]
    
    # 学生信息
    student = models.ForeignKey(StudentData, on_delete=models.CASCADE, verbose_name="学生", related_name="transfer_records")
    
    # 转学信息
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE_CHOICES, verbose_name="转学类型")
    transfer_date = models.DateField(verbose_name="转学日期")
    transfer_reason = models.TextField(verbose_name="转学原因")
    
    # 学校信息
    previous_school = models.CharField(max_length=100, verbose_name="原学校", blank=True, null=True)
    target_school = models.CharField(max_length=100, verbose_name="目标学校", blank=True, null=True)
    
    # 转入时的年级班级信息
    transfer_grade = models.CharField(max_length=10, verbose_name="转入年级", blank=True, null=True)
    transfer_class = models.CharField(max_length=20, verbose_name="转入班级", blank=True, null=True)
    
    # 转出目标学校的年级班级信息
    target_grade = models.CharField(max_length=10, verbose_name="目标年级", blank=True, null=True)
    target_class = models.CharField(max_length=20, verbose_name="目标班级", blank=True, null=True)
    
    # 目标学校联系信息
    target_school_contact = models.CharField(max_length=50, verbose_name="目标学校联系人", blank=True, null=True)
    target_school_phone = models.CharField(max_length=20, verbose_name="目标学校联系电话", blank=True, null=True)
    target_school_address = models.TextField(verbose_name="目标学校地址", blank=True, null=True)
    
    # 休学复学相关字段（新增）
    expected_resume_date = models.DateField(verbose_name="预期复学日期", blank=True, null=True)
    contact_person = models.CharField(max_length=50, verbose_name="联系人", blank=True, null=True)
    contact_phone = models.CharField(max_length=20, verbose_name="联系电话", blank=True, null=True)
    
    # 处理状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="处理状态")
    
    # 备注信息
    remarks = models.TextField(verbose_name="备注", blank=True, null=True)
    
    # 处理人信息
    processor = models.CharField(max_length=50, verbose_name="处理人", blank=True, null=True)
    process_time = models.DateTimeField(verbose_name="处理时间", blank=True, null=True)
    
    # 审批意见
    approval_notes = models.TextField(verbose_name="审批意见", blank=True, null=True)
    
    # 系统字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "转学记录"
        verbose_name_plural = "转学记录"
        db_table = "transfer_record"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.name} - {self.get_transfer_type_display()} - {self.transfer_date}"

class ImportLog(models.Model):
    """导入日志模型"""
    filename = models.CharField(max_length=255, verbose_name="文件名")
    total_records = models.IntegerField(verbose_name="总记录数")
    success_records = models.IntegerField(verbose_name="成功记录数")
    error_records = models.IntegerField(verbose_name="错误记录数")
    import_time = models.DateTimeField(auto_now_add=True, verbose_name="导入时间")
    errors = models.TextField(blank=True, verbose_name="错误信息")
    
    class Meta:
        verbose_name = "导入日志"
        verbose_name_plural = "导入日志"
        db_table = "import_log"
        ordering = ['-import_time']
    
    def __str__(self):
        return f"{self.filename} - {self.import_time.strftime('%Y-%m-%d %H:%M:%S')}"

# 在 backend/student_data/models.py 中添加以下模型

class Subject(models.Model):
    """科目模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name="科目名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="科目代码") 
    category = models.CharField(max_length=20, verbose_name="科目类别", choices=[
        ('main', '主科'),
        ('sub', '副科'),
        ('elective', '选修课')
    ], default='main')
    credit = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="学分", default=1.0)
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "科目"
        verbose_name_plural = "科目"
        db_table = "subject"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Exam(models.Model):
    """考试模型"""
    name = models.CharField(max_length=100, verbose_name="考试名称")
    exam_type = models.CharField(max_length=20, verbose_name="考试类型", choices=[
        ('midterm', '期中考试'),
        ('final', '期末考试'),
        ('monthly', '月考'),
        ('quiz', '小测'),
        ('homework', '作业')
    ])
    academic_year = models.CharField(max_length=20, verbose_name="学年")  # 如：2023-2024
    semester = models.CharField(max_length=10, verbose_name="学期", choices=[
        ('1', '第一学期'),
        ('2', '第二学期')
    ])
    exam_date = models.DateField(verbose_name="考试日期")
    total_score = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="总分", default=100.0)
    is_published = models.BooleanField(default=False, verbose_name="是否发布成绩")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "考试"
        verbose_name_plural = "考试"
        db_table = "exam"
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"{self.academic_year}-{self.get_semester_display()}-{self.name}"

class Grade(models.Model):
    """成绩模型"""
    student = models.ForeignKey(StudentData, on_delete=models.CASCADE, verbose_name="学生", related_name="grades")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="科目")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name="考试")
    score = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="分数")
    rank_in_class = models.IntegerField(null=True, blank=True, verbose_name="班级排名")
    rank_in_grade = models.IntegerField(null=True, blank=True, verbose_name="年级排名")
    
    # 🆕 新增字段：总分排名
    total_rank_in_class = models.IntegerField(null=True, blank=True, verbose_name="班级总分排名")
    total_rank_in_grade = models.IntegerField(null=True, blank=True, verbose_name="年级总分排名")
    
    remarks = models.TextField(blank=True, null=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "成绩"
        verbose_name_plural = "成绩"
        db_table = "grade"
        ordering = ['-exam__exam_date', 'student__school_id', 'subject__code']
        unique_together = ['student', 'subject', 'exam']
    
    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.score}分"
    
    def get_grade_level(self):
        """获取成绩等级"""
        score = float(self.score)
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
