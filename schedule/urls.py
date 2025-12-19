from django.urls import path
from . import views as schedule_views

urlpatterns = [
    path('', schedule_views.schedule_view, name='schedule'),
    path('download/', schedule_views.download_schedule_docx, name='schedule_download'),
    path('admin/manage/', schedule_views.admin_schedule_manage, name='admin_schedule_manage'),
    path('admin/create/<int:group_id>/', schedule_views.admin_schedule_create, name='admin_schedule_create'),
    path('admin/edit/<int:schedule_id>/', schedule_views.admin_schedule_edit, name='admin_schedule_edit'),
    path('admin/delete/<int:schedule_id>/', schedule_views.admin_schedule_delete, name='admin_schedule_delete'),
]
