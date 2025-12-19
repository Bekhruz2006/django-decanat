from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max

from main.models import User, Message, StudentProfile
from main.forms import MessageForm


@login_required
def chat_list(request):
    """Список контактов для чата"""
    user = request.user
    
    if user.role == 'student':
        # Студент видит своих преподавателей
        try:
            profile = user.student_profile
            group = profile.group
        except (StudentProfile.DoesNotExist, AttributeError):
            messages.error(request, 'У вас не указана группа')
            return redirect('home')
        
        # Получаем преподавателей, которые ведут предметы в группе студента
        teacher_ids = group.schedules.values_list('teacher_id', flat=True).distinct()
        contacts = User.objects.filter(id__in=teacher_ids, role='teacher')
        
    elif user.role in ['teacher', 'dean']:
        # Преподаватель видит студентов своих групп
        # Получаем группы, где преподаватель ведет занятия
        group_ids = user.schedule_set.values_list('group_id', flat=True).distinct()
        
        # Получаем студентов этих групп
        contacts = User.objects.filter(
            role='student',
            student_profile__group_id__in=group_ids
        ).order_by('full_name')
    
    else:
        contacts = User.objects.none()
    
    # Для каждого контакта получаем последнее сообщение и количество непрочитанных
    contacts_data = []
    for contact in contacts:
        # Последнее сообщение
        last_message = Message.objects.filter(
            Q(sender=user, recipient=contact) | Q(sender=contact, recipient=user)
        ).order_by('-created_at').first()
        
        # Непрочитанные сообщения от этого контакта
        unread_count = Message.objects.filter(
            sender=contact,
            recipient=user,
            is_read=False
        ).count()
        
        contacts_data.append({
            'contact': contact,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    return render(request, 'chat/chat_list.html', {'contacts_data': contacts_data})


@login_required
def chat_conversation(request, user_id):
    """Окно переписки с конкретным пользователем"""
    contact = get_object_or_404(User, id=user_id)
    user = request.user
    
    # Проверяем права доступа к чату
    can_chat = False
    
    if user.role == 'student':
        # Студент может общаться со своими преподавателями
        try:
            group = user.student_profile.group
            teacher_ids = group.schedules.values_list('teacher_id', flat=True)
            can_chat = contact.id in teacher_ids
        except (StudentProfile.DoesNotExist, AttributeError):
            pass
    
    elif user.role in ['teacher', 'dean']:
        # Преподаватель может общаться со студентами своих групп
        group_ids = user.schedule_set.values_list('group_id', flat=True)
        can_chat = contact.role == 'student' and contact.student_profile.group_id in group_ids
    
    if not can_chat:
        messages.error(request, 'У вас нет доступа к этому чату')
        return redirect('chat_list')
    
    # Получаем сообщения
    messages_list = Message.objects.filter(
        Q(sender=user, recipient=contact) | Q(sender=contact, recipient=user)
    ).order_by('created_at')
    
    # Отмечаем сообщения от контакта как прочитанные
    Message.objects.filter(
        sender=contact,
        recipient=user,
        is_read=False
    ).update(is_read=True)
    
    # Обработка отправки сообщения
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = user
            message.recipient = contact
            message.save()
            messages.success(request, 'Сообщение отправлено')
            return redirect('chat_conversation', user_id=contact.id)
    else:
        form = MessageForm()
    
    context = {
        'contact': contact,
        'messages_list': messages_list,
        'form': form,
    }
    
    return render(request, 'chat/chat_conversation.html', context)


@login_required
def chat_send_message(request, user_id):
    """AJAX: Отправка сообщения"""
    if request.method == 'POST':
        contact = get_object_or_404(User, id=user_id)
        content = request.POST.get('content')
        
        if content:
            message = Message.objects.create(
                sender=request.user,
                recipient=contact,
                content=content
            )
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'created_at': message.created_at.strftime('%H:%M'),
                    'sender': message.sender.full_name
                }
            })
    
    return JsonResponse({'success': False})


@login_required
def chat_get_messages(request, user_id):
    """AJAX: Получение новых сообщений"""
    contact = get_object_or_404(User, id=user_id)
    last_message_id = request.GET.get('last_id', 0)
    
    # Получаем новые сообщения
    new_messages = Message.objects.filter(
        Q(sender=request.user, recipient=contact) | Q(sender=contact, recipient=request.user),
        id__gt=last_message_id
    ).order_by('created_at')
    
    # Отмечаем как прочитанные
    Message.objects.filter(
        sender=contact,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    messages_data = []
    for msg in new_messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%H:%M'),
            'sender': msg.sender.full_name,
            'is_mine': msg.sender == request.user
        })
    
    return JsonResponse({
        'success': True,
        'messages': messages_data
    })