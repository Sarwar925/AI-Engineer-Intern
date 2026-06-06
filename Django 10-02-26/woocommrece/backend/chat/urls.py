from django.urls import path

from .views import chat_message, health_check

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("chat/", chat_message, name="chat-message"),
]

