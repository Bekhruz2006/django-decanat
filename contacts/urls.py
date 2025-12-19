from django.urls import path
from . import views as contacts_views

urlpatterns = [
    path('', contacts_views.contacts_view, name='contacts_view'),
    path('edit/', contacts_views.contacts_edit, name='contacts_edit'),
]
