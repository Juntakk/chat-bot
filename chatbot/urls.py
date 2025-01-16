from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'chatbot'  # This registers the namespace 'chatbot'

urlpatterns = [
   path('', views.chatbot_home, name='chatbot_home'),
]
