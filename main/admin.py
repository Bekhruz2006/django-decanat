from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Group, Subject, StudentProfile, Schedule,
    Attendance, AttendanceHistory, News, Contact, Message
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'full_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'full_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'full_name')
        }),
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'course']
    list_filter = ['course']
    search_fields = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']
    filter_horizontal = ['teachers']


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'student_id']
    list_filter = ['group']
    search_fields = ['user__full_name', 'student_id']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['group', 'subject', 'teacher', 'weekday', 'start_time', 'room']
    list_filter = ['group', 'weekday', 'subject']
    search_fields = ['group__name', 'subject__name', 'teacher__full_name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status', 'grade', 'teacher']
    list_filter = ['status', 'date', 'subject']
    search_fields = ['student__full_name', 'subject__name']
    date_hierarchy = 'date'


@admin.register(AttendanceHistory)
class AttendanceHistoryAdmin(admin.ModelAdmin):
    list_display = ['attendance', 'changed_by', 'changed_at', 'old_status', 'new_status']
    list_filter = ['changed_at']
    search_fields = ['attendance__student__full_name']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'phone', 'working_hours']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__full_name', 'recipient__full_name', 'content']
    date_hierarchy = 'created_at'