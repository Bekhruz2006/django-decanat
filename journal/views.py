from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from django.utils import timezone

from main.models import User, Group, Subject, Attendance, AttendanceHistory, StudentProfile


def is_teacher(user):
    return user.is_authenticated and user.role in ['teacher', 'dean']


def is_student(user):
    return user.is_authenticated and user.role == 'student'


@login_required
@user_passes_test(is_teacher)
def teacher_groups(request):
    """Список групп преподавателя"""
    # Получаем предметы, которые ведет преподаватель
    subjects = request.user.subjects_teaching.all().prefetch_related('schedules__group')
    
    # Собираем уникальные группы
    groups_dict = {}
    for subject in subjects:
        for schedule in subject.schedule_set.all():
            if schedule.group.id not in groups_dict:
                groups_dict[schedule.group.id] = {
                    'group': schedule.group,
                    'subjects': []
                }
            if subject not in groups_dict[schedule.group.id]['subjects']:
                groups_dict[schedule.group.id]['subjects'].append(subject)
    
    groups_list = list(groups_dict.values())
    
    return render(request, 'journal/teacher_groups.html', {'groups_list': groups_list})


@login_required
@user_passes_test(is_teacher)
def teacher_journal(request, group_id, subject_id):
    """Недельный журнал преподавателя"""
    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Проверяем, что преподаватель ведет этот предмет в этой группе
    if request.user.role == 'teacher' and subject not in request.user.subjects_teaching.all():
        messages.error(request, 'У вас нет доступа к этому журналу')
        return redirect('teacher_groups')
    
    # Получаем неделю
    week_offset = int(request.GET.get('week', 0))
    today = timezone.now().date()
    
    # Начало текущей недели (понедельник)
    current_week_start = today - timedelta(days=today.weekday())
    week_start = current_week_start + timedelta(weeks=week_offset)
    week_end = week_start + timedelta(days=6)
    
    # Получаем студентов группы
    students = User.objects.filter(
        role='student',
        student_profile__group=group
    ).order_by('full_name')
    
    # Получаем дни недели (только будние)
    week_days = []
    for i in range(5):  # Пн-Пт
        day = week_start + timedelta(days=i)
        week_days.append(day)
    
    # Формируем данные для журнала
    journal_data = []
    for student in students:
        student_row = {
            'student': student,
            'days': []
        }
        
        for day in week_days:
            # Получаем или создаем запись посещаемости
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                subject=subject,
                date=day,
                defaults={
                    'teacher': request.user,
                    'status': 'present',
                }
            )
            
            # Проверяем, можно ли редактировать (не старше 7 дней)
            can_edit = (today - day).days <= 7
            
            student_row['days'].append({
                'date': day,
                'attendance': attendance,
                'can_edit': can_edit
            })
        
        journal_data.append(student_row)
    
    context = {
        'group': group,
        'subject': subject,
        'week_start': week_start,
        'week_end': week_end,
        'week_days': week_days,
        'journal_data': journal_data,
        'week_offset': week_offset,
    }
    
    return render(request, 'journal/teacher_journal.html', context)


@login_required
@user_passes_test(is_teacher)
@require_POST
def update_attendance(request):
    """AJAX: Обновление посещаемости и оценки"""
    try:
        attendance_id = request.POST.get('attendance_id')
        field = request.POST.get('field')  # 'status' или 'grade'
        value = request.POST.get('value')
        
        attendance = get_object_or_404(Attendance, id=attendance_id)
        
        # Проверяем, можно ли редактировать (не старше 7 дней)
        today = timezone.now().date()
        if (today - attendance.date).days > 7:
            return JsonResponse({
                'success': False,
                'error': 'Редактирование возможно только в течение 7 дней'
            })
        
        # Сохраняем историю
        old_status = attendance.status
        old_grade = attendance.grade
        
        # Обновляем поле
        if field == 'status':
            attendance.status = value
        elif field == 'grade':
            attendance.grade = int(value) if value else None
        
        attendance.teacher = request.user
        attendance.save()
        
        # Создаем запись истории
        AttendanceHistory.objects.create(
            attendance=attendance,
            changed_by=request.user,
            old_status=old_status,
            new_status=attendance.status,
            old_grade=old_grade,
            new_grade=attendance.grade
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Сохранено'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@user_passes_test(is_teacher)
def attendance_history(request, attendance_id):
    """История изменений посещаемости"""
    attendance = get_object_or_404(Attendance, id=attendance_id)
    history = attendance.history.all()
    
    return render(request, 'journal/attendance_history.html', {
        'attendance': attendance,
        'history': history
    })


@login_required
@user_passes_test(is_student)
def student_journal(request):
    """Журнал студента (его оценки и посещаемость)"""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Профиль студента не найден')
        return redirect('home')
    
    # Получаем все записи посещаемости студента
    attendances = Attendance.objects.filter(
        student=request.user
    ).select_related('subject', 'teacher').order_by('-date')
    
    # Фильтр по предмету
    subject_id = request.GET.get('subject')
    if subject_id:
        attendances = attendances.filter(subject_id=subject_id)
    
    # Получаем список предметов для фильтра
    subjects = Subject.objects.filter(
        id__in=attendances.values_list('subject_id', flat=True).distinct()
    )
    
    context = {
        'attendances': attendances,
        'subjects': subjects,
        'selected_subject': subject_id,
    }
    
    return render(request, 'journal/student_journal.html', context)