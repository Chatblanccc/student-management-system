from django.contrib import admin
from .models import StudentData, TransferRecord, ImportLog, Subject, Exam, Grade

# Register your models here.

@admin.register(StudentData)
class StudentDataAdmin(admin.ModelAdmin):
    list_display = ['school_id', 'name', 'grade', 'class_name', 'status', 'created_at']
    list_filter = ['status', 'grade', 'class_name', 'created_at']
    search_fields = ['school_id', 'name', 'id_card']
    ordering = ['-created_at']

@admin.register(TransferRecord)
class TransferRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'transfer_type', 'transfer_date', 'status', 'created_at']
    list_filter = ['transfer_type', 'status', 'created_at']
    search_fields = ['student__name', 'student__school_id']
    ordering = ['-created_at']

@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ['filename', 'total_records', 'success_records', 'error_records', 'import_time']
    list_filter = ['import_time']
    ordering = ['-import_time']
    readonly_fields = ['filename', 'total_records', 'success_records', 'error_records', 'import_time', 'errors']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'credit', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['code']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'category', 'credit')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'academic_year', 'semester', 'exam_date', 'total_score', 'is_published']
    list_filter = ['exam_type', 'academic_year', 'semester', 'is_published', 'exam_date']
    search_fields = ['name', 'academic_year']
    ordering = ['-exam_date', 'academic_year', 'semester']
    
    fieldsets = (
        ('考试基本信息', {
            'fields': ('name', 'exam_type', 'exam_date', 'total_score')
        }),
        ('学年学期', {
            'fields': ('academic_year', 'semester')
        }),
        ('发布状态', {
            'fields': ('is_published',)
        }),
    )

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'exam', 'score', 'get_grade_level', 'rank_in_class', 'rank_in_grade']
    list_filter = ['exam', 'subject', 'exam__academic_year', 'exam__semester']
    search_fields = ['student__name', 'student__school_id', 'subject__name', 'exam__name']
    ordering = ['-exam__exam_date', 'student__school_id', 'subject__code']
    
    def get_grade_level(self, obj):
        return obj.get_grade_level()
    get_grade_level.short_description = '等级'
