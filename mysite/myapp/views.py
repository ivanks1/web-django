from urllib import request
from django.shortcuts import render
from .models import UserProfiles
from datetime import datetime 
import random

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def user_profile(request, username):
    user = UserProfiles.get(username)


    if datetime.now().hour < 12: # datetime.now().hour - узнать текущий час
        hello_message = "Доброе утро" # новая переменная с приветствием в зависимости от времени суток
    elif datetime.now().hour < 18:
        hello_message = "Добрый день"
    elif datetime.now().hour < 22:
        hello_message = "Добрый вечер"
    else:
        hello_message = "Доброй ночи"

    email = username + '@gmail.com' # формируем email на основе имени пользователя

    is_online = random.random() < 0.5

    if user is None: # если пользователь не найден в базе данных (models.py)
        return render(request, 'user_profile.html', {
            'username': '?',
            'age': '?',
            'city': '?',
            'ip_address': '?',
            'about_me': '?',
            'hello_message': hello_message,
            'email': email,
            'is_online': False
        })

    return render(request, 'user_profile.html', { # если пользователь найден в базе данных (models.py)
        'username': user['username'],
        'age': user['age'],
        'city': user['city'],
        'ip_address': user['ip_address'],
        'about_me': user['about_me'],
        'hello_message': hello_message,
        'email': email,
        'is_online': is_online
    })
