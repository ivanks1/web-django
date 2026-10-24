from django.db import models


class UserProfiles(models.Model):
    username = models.SlugField("Имя в URL", max_length=100, unique=True, allow_unicode=True)
    display_name = models.CharField("Отображаемое имя", max_length=150, default="")
    age = models.CharField("Возраст", max_length=50, help_text="Например: 25 или ≈ 25")
    city = models.CharField("Город", max_length=150)
    ip_address = models.GenericIPAddressField("IP-адрес")
    about_me = models.TextField("О себе")
    email = models.EmailField("Email", blank=True)

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
        ordering = ("username",)

    def __str__(self):
        return f"{self.display_name} ({self.username})"



class Resume(models.Model):
    surname = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField()
    profession = models.CharField(max_length=150)
    skills = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
            verbose_name = "Резюме"
            verbose_name_plural = "Резюме"
            ordering = ("surname", "name",)

    def __str__(self):
        return f"{self.surname} {self.name}"
