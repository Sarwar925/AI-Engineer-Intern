"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from api.views import agent_chat

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/chat/', agent_chat, name='agent_chat'), # This means every URL starts with /api/
]
# from django.contrib import admin
# from django.urls import path
# from api.views import agent_chat, login, signup, get_users, create_user, update_user, delete_user

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include('api.urls')),
#     path('api/login/', login),
#     path('api/signup/', signup),
#     path('api/users/', get_users),
#     path('api/create-user/', create_user),
#     path('api/update-user/<int:id>/', update_user),
#     path('api/delete-user/<int:id>/', delete_user),
#     path('api/agent-chat/', agent_chat),  # ✅ This line is critical
# ]
