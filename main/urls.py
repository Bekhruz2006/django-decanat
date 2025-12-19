from django.urls import path
from . import views

urlpatterns = [
    # Главная и аутентификация
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Профиль студента
    path('profile/', views.student_profile, name='student_profile'),
    path('profile/edit/', views.student_profile_edit, name='student_profile_edit'),
    
    # Админ-панель декана
    path('admin/panel/', views.admin_panel, name='admin_panel'),
    
    # Управление пользователями
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:user_id>/reset-password/', views.admin_user_reset_password, name='admin_user_reset_password'),
    
    # Управление группами
    path('admin/groups/', views.admin_groups, name='admin_groups'),
    path('admin/groups/create/', views.admin_group_create, name='admin_group_create'),
    path('admin/groups/<int:group_id>/edit/', views.admin_group_edit, name='admin_group_edit'),
    
    # Управление предметами
    path('admin/subjects/', views.admin_subjects, name='admin_subjects'),
    path('admin/subjects/create/', views.admin_subject_create, name='admin_subject_create'),
    path('admin/subjects/<int:subject_id>/edit/', views.admin_subject_edit, name='admin_subject_edit'),
]