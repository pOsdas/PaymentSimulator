from django.urls import path
from .views import UserInfoView, ChangeUserView, CreateUserView, DeleteUserView, UsersListView

urlpatterns = [
    # Пользователи
    path('user-info/', UserInfoView.as_view(), name='user_info'),
    path('get-users/', UsersListView.as_view(), name='get-users'),
    path('delete-user/', DeleteUserView.as_view(), name='delete-user'),
    path('change-user/', ChangeUserView.as_view(), name='change-user'),
    path('create-user/', CreateUserView.as_view(), name='create-user')
]
