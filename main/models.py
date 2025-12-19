from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """Расширенная модель пользователя с ролями"""
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('dean', 'Декан'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='Роль'
    )
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"


class Group(models.Model):
    """Группа студентов"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название группы')
    course = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name='Курс'
    )
    
    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['course', 'name']
    
    def __str__(self):
        return self.name


class Subject(models.Model):
    """Предмет/дисциплина"""
    name = models.CharField(max_length=200, verbose_name='Название предмета')
    code = models.CharField(max_length=50, unique=True, verbose_name='Код предмета')
    teachers = models.ManyToManyField(
        User,
        limit_choices_to={'role': 'teacher'},
        related_name='subjects_teaching',
        verbose_name='Преподаватели'
    )
    
    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    """Профиль студента с дополнительной информацией"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': 'student'}
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        related_name='students',
        verbose_name='Группа'
    )
    student_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Номер зачетки'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.TextField(blank=True, verbose_name='Адрес')
    photo = models.ImageField(
        upload_to='student_photos/',
        blank=True,
        null=True,
        verbose_name='Фото'
    )
    
    class Meta:
        verbose_name = 'Профиль студента'
        verbose_name_plural = 'Профили студентов'
    
    def __str__(self):
        return f"Профиль {self.user.full_name}"


class Schedule(models.Model):
    """Расписание занятий"""
    WEEKDAY_CHOICES = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
    ]
    
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Группа'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        verbose_name='Предмет'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        verbose_name='Преподаватель'
    )
    weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        verbose_name='День недели'
    )
    start_time = models.TimeField(verbose_name='Время начала')
    end_time = models.TimeField(verbose_name='Время окончания')
    room = models.CharField(max_length=50, verbose_name='Аудитория')
    
    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'
        ordering = ['weekday', 'start_time']
        unique_together = ['group', 'weekday', 'start_time']
    
    def __str__(self):
        return f"{self.group} - {self.subject} ({self.get_weekday_display()})"


class Attendance(models.Model):
    """Посещаемость и оценки"""
    STATUS_CHOICES = [
        ('present', 'Б (Был)'),
        ('absent', 'Н (Не был)'),
    ]
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='attendances',
        verbose_name='Студент'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        verbose_name='Предмет'
    )
    date = models.DateField(verbose_name='Дата')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='present',
        verbose_name='Статус'
    )
    grade = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name='Балл'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='attendance_records',
        verbose_name='Преподаватель'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'
        unique_together = ['student', 'subject', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.subject} ({self.date})"


class AttendanceHistory(models.Model):
    """История изменений посещаемости"""
    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Запись посещаемости'
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Кто изменил'
    )
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='Когда')
    old_status = models.CharField(max_length=10, blank=True, verbose_name='Старый статус')
    new_status = models.CharField(max_length=10, verbose_name='Новый статус')
    old_grade = models.IntegerField(null=True, blank=True, verbose_name='Старый балл')
    new_grade = models.IntegerField(null=True, blank=True, verbose_name='Новый балл')
    
    class Meta:
        verbose_name = 'История изменений'
        verbose_name_plural = 'История изменений'
        ordering = ['-changed_at']


class News(models.Model):
    """Новости кафедры"""
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Текст')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'dean'},
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Contact(models.Model):
    """Контактная информация деканата (одна запись)"""
    address = models.TextField(verbose_name='Адрес')
    phone = models.CharField(max_length=50, verbose_name='Телефон')
    telegram = models.CharField(max_length=100, blank=True, verbose_name='Telegram')
    whatsapp = models.CharField(max_length=50, blank=True, verbose_name='WhatsApp')
    working_hours = models.CharField(max_length=200, verbose_name='Время работы')
    room_number = models.CharField(max_length=50, verbose_name='Номер кабинета')
    
    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'
    
    def __str__(self):
        return f"Контакты деканата ({self.room_number})"
    
    @classmethod
    def get_contact(cls):
        """Получить или создать единственную запись контактов"""
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'address': 'г. Душанбе, ул. Университетская, 1',
                'phone': '+992 123 456789',
                'telegram': '@dekanat',
                'whatsapp': '+992123456789',
                'working_hours': 'Пн-Пт: 9:00-17:00',
                'room_number': '101'
            }
        )
        return obj


class Message(models.Model):
    """Сообщения в чате"""
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Отправитель'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Получатель'
    )
    content = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.content[:30]}"