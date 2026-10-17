from django.contrib import admin
from django.urls import path
from myapp import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('user/', views.user_profile, name='user_profile', kwargs={'username': 'Гость'}),
    path('jinja/', views.about_jinja, name='about_jinja')
]