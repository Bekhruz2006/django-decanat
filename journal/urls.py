from django.urls import path
from . import views as journal_views

urlpatterns = [
    path('teacher/groups/', journal_views.teacher_groups, name='teacher_groups'),
    path('teacher/<int:group_id>/<int:subject_id>/', journal_views.teacher_journal, name='teacher_journal'),
    path('teacher/update/', journal_views.update_attendance, name='update_attendance'),
    path('teacher/history/<int:attendance_id>/', journal_views.attendance_history, name='attendance_history'),
    path('student/', journal_views.student_journal, name='student_journal'),
]
