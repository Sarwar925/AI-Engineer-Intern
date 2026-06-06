# urls.py
from django.urls import path
from .views import chat_agent
from .views import Register
from .views import LoginView
from .views import ProfileView
from .views import UserListView
from .views import product_list
from .views import product_view
from .views import product_del_view
from .views import product_update_view
from .views import add_product_view
from .views import update_user_view
from .views import delete_user_view
from .views import LogoutView
from .views import AuthCheck
from .views import set_role_view
from .views import knowledge_base_upload
from .views import knowledge_base_search
from .views import knowledge_base_docs
from .views import knowledge_base_delete
from .views import email_automation_run
from .views import email_automation_config
urlpatterns = [
    path("chat/", chat_agent, name="chat_agent"),
    path("email-automation/run/", email_automation_run, name="email-automation-run"),
    path("email-automation/config/", email_automation_config, name="email-automation-config"),
    path("knowledge-base/upload/", knowledge_base_upload, name="knowledge-base-upload"),
    path("knowledge-base/search/", knowledge_base_search, name="knowledge-base-search"),
    path("knowledge-base/docs/", knowledge_base_docs, name="knowledge-base-docs"),
    path("knowledge-base/delete/<str:document_id>/", knowledge_base_delete, name="knowledge-base-delete"),
    path('register/',Register.as_view()),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('profile/', ProfileView.as_view()),
    path('users/', UserListView.as_view(), name='user-list'),
    path('products/', product_list),
    path('product-view/<int:id>/', product_view),
    path('product-del/<int:id>/', product_del_view),
    path('product-update/<int:id>/', product_update_view),
    path('add-product/', add_product_view),
    path('update-user/<int:id>/', update_user_view),
    path('delete-user/<int:id>/', delete_user_view),
    path("auth-check/", AuthCheck.as_view()),
    path("set-role/<int:id>/", set_role_view),
]
