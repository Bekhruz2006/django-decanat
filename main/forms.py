from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    User, Group, Subject, StudentProfile, Schedule, 
    Attendance, News, Contact, Message
)


class LoginForm(AuthenticationForm):
    """Форма входа"""
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите логин'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль'
        })
    )


class QuickUserCreateForm(forms.ModelForm):
    """Форма быстрого создания пользователя"""
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label='Группа',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    student_id = forms.CharField(
        required=False,
        label='Номер зачетки',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'full_name', 'role', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Если студент, создаем профиль
            if user.role == 'student':
                StudentProfile.objects.create(
                    user=user,
                    group=self.cleaned_data.get('group'),
                    student_id=self.cleaned_data.get('student_id', f'STD{user.id}')
                )
        return user


class UserEditForm(forms.ModelForm):
    """Форма редактирования пользователя"""
    class Meta:
        model = User
        fields = ['username', 'full_name', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }


class GroupForm(forms.ModelForm):
    """Форма создания/редактирования группы"""
    class Meta:
        model = Group
        fields = ['name', 'course']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'course': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class SubjectForm(forms.ModelForm):
    """Форма создания/редактирования предмета"""
    class Meta:
        model = Subject
        fields = ['name', 'code', 'teachers']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'code': forms.TextInput(attrs={'class': 'form-input'}),
            'teachers': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


class ScheduleForm(forms.ModelForm):
    """Форма создания/редактирования расписания"""
    class Meta:
        model = Schedule
        fields = ['group', 'subject', 'teacher', 'weekday', 'start_time', 'end_time', 'room']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'weekday': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'room': forms.TextInput(attrs={'class': 'form-input'}),
        }


class AttendanceForm(forms.ModelForm):
    """Форма для посещаемости и оценок"""
    class Meta:
        model = Attendance
        fields = ['status', 'grade']
        widgets = {
            'status': forms.Select(attrs={'class': 'attendance-status'}),
            'grade': forms.NumberInput(attrs={
                'class': 'attendance-grade',
                'min': '1',
                'max': '12'
            }),
        }


class StudentProfileEditForm(forms.ModelForm):
    """Форма редактирования профиля студента"""
    class Meta:
        model = StudentProfile
        fields = ['phone', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class NewsForm(forms.ModelForm):
    """Форма создания/редактирования новости"""
    class Meta:
        model = News
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 6}),
        }


class ContactForm(forms.ModelForm):
    """Форма редактирования контактов"""
    class Meta:
        model = Contact
        fields = ['address', 'phone', 'telegram', 'whatsapp', 'working_hours', 'room_number']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'telegram': forms.TextInput(attrs={'class': 'form-input'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-input'}),
            'working_hours': forms.TextInput(attrs={'class': 'form-input'}),
            'room_number': forms.TextInput(attrs={'class': 'form-input'}),
        }


class MessageForm(forms.ModelForm):
    """Форма отправки сообщения"""
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'message-input',
                'rows': 3,
                'placeholder': 'Введите сообщение...'
            }),
        }