from django.db import migrations


def seed_profiles(apps, schema_editor):
    UserProfiles = apps.get_model("myapp", "UserProfiles")
    profiles = UserProfiles.objects.using(schema_editor.connection.alias)
    for profile in profiles.filter(display_name=""):
        profile.display_name = profile.username
        profile.save(using=schema_editor.connection.alias, update_fields=["display_name"])
    initial_profiles = [
        ("Ivan", "Иван/Ваня", "≈ 13", "Алматы", "12.51.0.1",
         "Привет! Я увлекаюсь программированием и изучаю Python, HTML, CSS. Люблю создавать веб-приложения и сайты."),
        ("Dima", "Дима/Дмитрий", "≈ 45", "Moscow", "2.132.44.38",
         "Программист, увлекаюсь разработкой веб-приложений и изучением новых технологий. Люблю делиться знаниями с другими и помогать новичкам в программировании."),
        ("Sergey", "Сергей/Серёжа", "≈ 25", "Алматы", "6.23.1.45",
         "Веб-программист, увлекаюсь разработкой игр и веб-приложений. Люблю изучать новые технологии и делиться знаниями с другими."),
    ]
    for username, display_name, age, city, ip_address, about_me in initial_profiles:
        profiles.get_or_create(username=username, defaults={
            "display_name": display_name, "age": age, "city": city,
            "ip_address": ip_address, "about_me": about_me,
            "email": f"{username}@gmail.com",
        })


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0003_alter_userprofiles_options_userprofiles_display_name_and_more"),
    ]
    operations = [migrations.RunPython(seed_profiles, migrations.RunPython.noop)]
