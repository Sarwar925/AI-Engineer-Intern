from django.urls import path
from .views import signup, login, get_users, create_user, update_user, delete_user,agent_chat

urlpatterns = [
    path('signup/', signup), # Result: /api/signup/
    path('login/', login),   # Result: /api/login/
    path('users/', get_users),
    path('create-user/', create_user),
    path('update-user/<int:id>/', update_user),
    path('delete-user/<int:id>/', delete_user),
    path('api/chat/', agent_chat, name='agent_chat'),

]
