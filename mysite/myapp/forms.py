from django import forms


class NumberRangeForm(forms.Form):
    number_type = forms.ChoiceField(
        label="Какие числа отобразить?",
        choices=[("even", "Чётные"), ("odd", "Нечётные"),
        ("prime", "Простые"), ("all", "Все")],
        widget=forms.RadioSelect,
        initial="all",
        error_messages={"required": "Выберите тип чисел.",
                        "invalid_choice": "Выберите один из предложенных вариантов."},
    )
    start = forms.IntegerField(label="От", initial=1, min_value=-1000000, max_value=1000000)
    end = forms.IntegerField(label="До", initial=20, min_value=-1000000, max_value=1000000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("start", "end"):
            self.fields[name].error_messages.update({
                "required": "Укажите границу диапазона.",
                "invalid": "Введите целое число.",
                "min_value": "Число должно быть не меньше −1 000 000.",
                "max_value": "Число должно быть не больше 1 000 000.",
            })

    def clean(self):
        data = super().clean()
        start, end = data.get("start"), data.get("end")
        if start is not None and end is not None:
            if start > end:
                raise forms.ValidationError("Начало диапазона должно быть не больше конца.")
            if end - start + 1 > 1000:
                raise forms.ValidationError("Выберите диапазон не более чем из 1000 чисел.")
        return data


class ResumeForm(forms.Form):
    surname = forms.CharField(label="Фамилия", max_length=100)
    name = forms.CharField(label="Имя", max_length=100)
    age = forms.IntegerField(label="Возраст", min_value=0, max_value=99)
    profession = forms.CharField(label="Профессия", max_length=150)
    skills = forms.CharField(label="Навыки", max_length=1000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "surname": "Иванов",
            "name": "Иван",
            "age": "0–99",
            "profession": "Программист",
            "skills": "C++, Python",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "autoExpand gap",
                "placeholder": placeholders[name],
            })
            field.error_messages["required"] = "Заполните это поле."
        self.fields["age"].error_messages.update({
            "invalid": "Введите целый возраст.",
            "min_value": "Возраст должен быть не меньше 0.",
            "max_value": "Возраст должен быть не больше 99.",
        })
