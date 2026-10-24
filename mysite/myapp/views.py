from django.forms.models import model_to_dict
from django.shortcuts import redirect, render
from .forms import NumberRangeForm, ResumeForm
from .numbers import select_numbers
from datetime import datetime 
import random
from .models import UserProfiles, Resume

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def user_profile(request, username):  # функция для отображения страницы профиля пользователя
    user = UserProfiles.objects.filter(username=username).first()

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

    if user is None: # если пользователь не найден в базе данных
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

    return render(request, 'user_profile.html', { # если пользователь найден в базе данных
        'username': user.display_name,
        'age': user.age,
        'city': user.city,
        'ip_address': user.ip_address,
        'about_me': user.about_me,
        'hello_message': hello_message,
        'email': user.email,
        'is_online': is_online
        
    })

def about_jinja(request):  # функция для отображения страницы "Jinja"
    form = ResumeForm(request.POST if request.method == "POST" else None)
    range_requested = any(key in request.GET for key in ("number_type", "start", "end"))
    number_form = NumberRangeForm(request.GET if range_requested else None)
    context = {"form": form, "number_form": number_form}
    if request.method == "GET":
        resume_id = request.session.get("last_resume_id")
        if resume_id is not None:
            resume = Resume.objects.filter(pk=resume_id).first()
            if resume is not None:
                context["resume"] = resume
                context["form"] = ResumeForm(initial=model_to_dict(resume))
    if range_requested and number_form.is_valid():
        data = number_form.cleaned_data
        context["numbers"] = select_numbers(data["start"], data["end"], data["number_type"])
        context["numbers_ready"] = True
    if request.method == "POST" and form.is_valid():
        resume = Resume.objects.create(**form.cleaned_data)
        request.session["last_resume_id"] = resume.pk
        return redirect("about_jinja")
    return render(request, 'about_jinja.html', context)
    
