from django.urls import path
from .views import index, login_view, logout_view, register_view, send_message, get_messages

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('send/', send_message, name='send_message'),
    path('messages/', get_messages, name='get_messages'),
]