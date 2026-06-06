from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat_history),
    path("chat/message/", views.chat_message),
]
