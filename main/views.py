from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q

from .models import User, Group, Subject, StudentProfile, News, Contact
from .forms import LoginForm, QuickUserCreateForm, UserEditForm, GroupForm, SubjectForm


def home(request):
    """Главная страница"""
    news_list = News.objects.all()[:5]
    contact = Contact.get_contact()
    
    context = {
        'news_list': news_list,
        'contact': contact,
    }
    return render(request, 'main/home.html', context)


def user_login(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.full_name}!')
            return redirect('home')
    else:
        form = LoginForm()
    
    return render(request, 'main/login.html', {'form': form})


@login_required
def user_logout(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')


def is_dean(user):
    """Проверка, является ли пользователь деканом"""
    return user.is_authenticated and user.role == 'dean'


def is_teacher(user):
    """Проверка, является ли пользователь преподавателем"""
    return user.is_authenticated and user.role in ['teacher', 'dean']


def is_student(user):
    """Проверка, является ли пользователь студентом"""
    return user.is_authenticated and user.role == 'student'


@login_required
@user_passes_test(is_dean)
def admin_panel(request):
    """Админ-панель декана"""
    return render(request, 'main/admin/dashboard.html')


@login_required
@user_passes_test(is_dean)
def admin_users(request):
    """Управление пользователями"""
    users = User.objects.all().select_related('student_profile')
    role_filter = request.GET.get('role')
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    context = {
        'users': users,
        'role_filter': role_filter,
    }
    return render(request, 'main/admin/users.html', context)


@login_required
@user_passes_test(is_dean)
def admin_user_create(request):
    """Быстрое создание пользователя"""
    if request.method == 'POST':
        form = QuickUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Пользователь {user.full_name} успешно создан!')
            return redirect('admin_users')
    else:
        form = QuickUserCreateForm()
    
    return render(request, 'main/admin/user_create.html', {'form': form})


@login_required
@user_passes_test(is_dean)
def admin_user_edit(request, user_id):
    """Редактирование пользователя"""
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пользователь обновлен!')
            return redirect('admin_users')
    else:
        form = UserEditForm(instance=user_obj)
    
    return render(request, 'main/admin/user_edit.html', {
        'form': form,
        'user_obj': user_obj
    })


@login_required
@user_passes_test(is_dean)
def admin_user_reset_password(request, user_id):
    """Сброс пароля пользователя"""
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if new_password:
            user_obj.set_password(new_password)
            user_obj.save()
            messages.success(request, f'Пароль для {user_obj.full_name} изменен!')
    
    return redirect('admin_users')


@login_required
@user_passes_test(is_dean)
def admin_groups(request):
    """Управление группами"""
    groups = Group.objects.all().prefetch_related('students')
    return render(request, 'main/admin/groups.html', {'groups': groups})


@login_required
@user_passes_test(is_dean)
def admin_group_create(request):
    """Создание группы"""
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Группа {group.name} создана!')
            return redirect('admin_groups')
    else:
        form = GroupForm()
    
    return render(request, 'main/admin/group_form.html', {'form': form})


@login_required
@user_passes_test(is_dean)
def admin_group_edit(request, group_id):
    """Редактирование группы"""
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Группа обновлена!')
            return redirect('admin_groups')
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'main/admin/group_form.html', {
        'form': form,
        'group': group
    })


@login_required
@user_passes_test(is_dean)
def admin_subjects(request):
    """Управление предметами"""
    subjects = Subject.objects.all().prefetch_related('teachers')
    return render(request, 'main/admin/subjects.html', {'subjects': subjects})


@login_required
@user_passes_test(is_dean)
def admin_subject_create(request):
    """Создание предмета"""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Предмет {subject.name} создан!')
            return redirect('admin_subjects')
    else:
        form = SubjectForm()
    
    return render(request, 'main/admin/subject_form.html', {'form': form})


@login_required
@user_passes_test(is_dean)
def admin_subject_edit(request, subject_id):
    """Редактирование предмета"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Предмет обновлен!')
            return redirect('admin_subjects')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'main/admin/subject_form.html', {
        'form': form,
        'subject': subject
    })


@login_required
@user_passes_test(is_student)
def student_profile(request):
    """Личный профиль студента"""
    from django.db.models import Count, Q
    from journal.models import Attendance
    from datetime import datetime, timedelta
    
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Профиль студента не найден')
        return redirect('home')
    
    # Статистика посещаемости
    total_absences = Attendance.objects.filter(
        student=request.user,
        status='absent'
    ).count()
    
    # Посещаемость по неделям (последние 12 недель)
    weekly_stats = []
    today = datetime.now().date()
    
    for i in range(11, -1, -1):
        week_start = today - timedelta(days=today.weekday() + i * 7)
        week_end = week_start + timedelta(days=6)
        
        total = Attendance.objects.filter(
            student=request.user,
            date__range=[week_start, week_end]
        ).count()
        
        present = Attendance.objects.filter(
            student=request.user,
            date__range=[week_start, week_end],
            status='present'
        ).count()
        
        percentage = (present / total * 100) if total > 0 else 100
        
        weekly_stats.append({
            'week': f'{week_start.strftime("%d.%m")}',
            'percentage': round(percentage, 1)
        })
    
    # Календарь посещаемости (последние 60 дней)
    calendar_data = []
    for i in range(60):
        day = today - timedelta(days=i)
        attendances = Attendance.objects.filter(
            student=request.user,
            date=day
        )
        
        if attendances.exists():
            has_absent = attendances.filter(status='absent').exists()
            if has_absent and attendances.count() == attendances.filter(status='absent').count():
                status = 'red'  # Не был ни на чем
            elif has_absent:
                status = 'yellow'  # Были пропуски
            else:
                status = 'green'  # Был на всех
            
            subjects_info = []
            for att in attendances:
                subjects_info.append(f"{att.subject.name}: {att.get_status_display()}")
            
            calendar_data.append({
                'date': day,
                'status': status,
                'info': '; '.join(subjects_info)
            })
    
    context = {
        'profile': profile,
        'total_absences': total_absences,
        'weekly_stats': weekly_stats,
        'calendar_data': calendar_data,
    }
    
    return render(request, 'main/student_profile.html', context)


@login_required
@user_passes_test(is_student)
def student_profile_edit(request):
    """Редактирование профиля студента"""
    from .forms import StudentProfileEditForm
    
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Профиль студента не найден')
        return redirect('home')
    
    if request.method == 'POST':
        form = StudentProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('student_profile')
    else:
        form = StudentProfileEditForm(instance=profile)
    
    return render(request, 'main/student_profile_edit.html', {'form': form})