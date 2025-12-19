from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime, timedelta
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from main.models import Schedule, Group, StudentProfile
from main.forms import ScheduleForm


def is_dean(user):
    return user.is_authenticated and user.role == 'dean'


def is_student(user):
    return user.is_authenticated and user.role == 'student'


@login_required
def schedule_view(request):
    """Просмотр расписания"""
    user = request.user
    
    # Для студента показываем расписание его группы
    if user.role == 'student':
        try:
            group = user.student_profile.group
        except (StudentProfile.DoesNotExist, AttributeError):
            messages.error(request, 'У вас не указана группа')
            return redirect('home')
        
        # Получаем неделю (текущая или следующая)
        week_offset = int(request.GET.get('week', 0))
        
        # Расписание группы
        schedules = Schedule.objects.filter(group=group).order_by('weekday', 'start_time')
        
        # Группируем по дням недели
        schedule_by_day = {}
        for i in range(1, 7):
            schedule_by_day[i] = schedules.filter(weekday=i)
        
        context = {
            'group': group,
            'schedule_by_day': schedule_by_day,
            'week_offset': week_offset,
            'weekdays': Schedule.WEEKDAY_CHOICES,
        }
        return render(request, 'schedule/student_schedule.html', context)
    
    # Для преподавателя показываем его расписание
    elif user.role == 'teacher':
        schedules = Schedule.objects.filter(teacher=user).order_by('weekday', 'start_time')
        
        schedule_by_day = {}
        for i in range(1, 7):
            schedule_by_day[i] = schedules.filter(weekday=i)
        
        context = {
            'schedule_by_day': schedule_by_day,
            'weekdays': Schedule.WEEKDAY_CHOICES,
        }
        return render(request, 'schedule/teacher_schedule.html', context)
    
    # Для декана
    else:
        groups = Group.objects.all()
        return render(request, 'schedule/dean_schedule.html', {'groups': groups})


@login_required
def download_schedule_docx(request):
    """Скачать расписание в формате DOCX"""
    user = request.user
    
    if user.role != 'student':
        messages.error(request, 'Доступно только для студентов')
        return redirect('schedule')
    
    try:
        group = user.student_profile.group
    except (StudentProfile.DoesNotExist, AttributeError):
        messages.error(request, 'У вас не указана группа')
        return redirect('schedule')
    
    # Создаем документ
    doc = Document()
    
    # Заголовок
    title = doc.add_heading(f'Расписание группы {group.name}', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Получаем расписание
    schedules = Schedule.objects.filter(group=group).order_by('weekday', 'start_time')
    
    # Создаем таблицу
    for day_num, day_name in Schedule.WEEKDAY_CHOICES:
        day_schedules = schedules.filter(weekday=day_num)
        
        if day_schedules.exists():
            # Добавляем день недели
            doc.add_heading(day_name, level=2)
            
            # Создаем таблицу для дня
            table = doc.add_table(rows=1, cols=4)
            table.style = 'Light Grid Accent 1'
            
            # Заголовки
            header_cells = table.rows[0].cells
            header_cells[0].text = 'Время'
            header_cells[1].text = 'Предмет'
            header_cells[2].text = 'Преподаватель'
            header_cells[3].text = 'Аудитория'
            
            # Данные
            for sched in day_schedules:
                row_cells = table.add_row().cells
                row_cells[0].text = f"{sched.start_time.strftime('%H:%M')} - {sched.end_time.strftime('%H:%M')}"
                row_cells[1].text = sched.subject.name
                row_cells[2].text = sched.teacher.full_name
                row_cells[3].text = sched.room
            
            doc.add_paragraph()  # Пустая строка
    
    # Сохраняем в HTTP ответ
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename=schedule_{group.name}.docx'
    doc.save(response)
    
    return response


@login_required
@user_passes_test(is_dean)
def admin_schedule_manage(request):
    """Управление расписанием (для декана)"""
    group_id = request.GET.get('group')
    
    if group_id:
        group = get_object_or_404(Group, id=group_id)
        schedules = Schedule.objects.filter(group=group).order_by('weekday', 'start_time')
        
        schedule_by_day = {}
        for i in range(1, 7):
            schedule_by_day[i] = schedules.filter(weekday=i)
        
        context = {
            'group': group,
            'schedule_by_day': schedule_by_day,
            'weekdays': Schedule.WEEKDAY_CHOICES,
        }
        return render(request, 'schedule/admin_schedule_edit.html', context)
    
    groups = Group.objects.all()
    return render(request, 'schedule/admin_schedule_select.html', {'groups': groups})


@login_required
@user_passes_test(is_dean)
def admin_schedule_create(request, group_id):
    """Создание занятия в расписании"""
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            messages.success(request, 'Занятие добавлено в расписание!')
            return redirect(f'/schedule/admin/manage/?group={group_id}')
    else:
        form = ScheduleForm(initial={'group': group})
    
    return render(request, 'schedule/admin_schedule_form.html', {
        'form': form,
        'group': group
    })


@login_required
@user_passes_test(is_dean)
def admin_schedule_edit(request, schedule_id):
    """Редактирование занятия в расписании"""
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Занятие обновлено!')
            return redirect(f'/schedule/admin/manage/?group={schedule.group.id}')
    else:
        form = ScheduleForm(instance=schedule)
    
    return render(request, 'schedule/admin_schedule_form.html', {
        'form': form,
        'schedule': schedule
    })


@login_required
@user_passes_test(is_dean)
def admin_schedule_delete(request, schedule_id):
    """Удаление занятия из расписания"""
    schedule = get_object_or_404(Schedule, id=schedule_id)
    group_id = schedule.group.id
    schedule.delete()
    messages.success(request, 'Занятие удалено из расписания')
    return redirect(f'/schedule/admin/manage/?group={group_id}')