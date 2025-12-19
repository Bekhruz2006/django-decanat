from django.urls import path
from . import views as news_views

urlpatterns = [
    path('', news_views.news_list, name='news_list'),
    path('<int:news_id>/', news_views.news_detail, name='news_detail'),
    path('create/', news_views.news_create, name='news_create'),
    path('<int:news_id>/edit/', news_views.news_edit, name='news_edit'),
    path('<int:news_id>/delete/', news_views.news_delete, name='news_delete'),
]
