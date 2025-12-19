from django.urls import path
from . import views as chat_views

urlpatterns = [
    path('', chat_views.chat_list, name='chat_list'),
    path('<int:user_id>/', chat_views.chat_conversation, name='chat_conversation'),
    path('<int:user_id>/send/', chat_views.chat_send_message, name='chat_send_message'),
    path('<int:user_id>/get/', chat_views.chat_get_messages, name='chat_get_messages'),
]
