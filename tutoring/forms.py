from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Course, TutoringHour


class TASignUpForm(UserCreationForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Which courses can you tutor?",
    )

    WEEKDAY_CHOICES = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]

    tutoring_day = forms.ChoiceField(
        choices=WEEKDAY_CHOICES,
        required=False,
        label="Tutoring Day",
    )

    tutoring_start = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        required=False,
        label="Start Time",
    )

    tutoring_end = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        required=False,
        label="End Time",
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")

    def clean(self):
        cleaned_data = super().clean()

        day = cleaned_data.get("tutoring_day")
        start = cleaned_data.get("tutoring_start")
        end = cleaned_data.get("tutoring_end")

        if any([day, start, end]):
            if not all([day, start, end]):
                raise forms.ValidationError(
                    "Please provide a day, start time, and end time."
                )

            if end <= start:
                raise forms.ValidationError("End time must be later than start time.")

        return cleaned_data


class TutoringHourForm(forms.ModelForm):
    weekday = forms.ChoiceField(
        choices=[("", "Select a day")] + TASignUpForm.WEEKDAY_CHOICES,
        required=True,
        label="Tutoring Day",
    )

    class Meta:
        model = TutoringHour
        fields = ("weekday", "start_time", "end_time")
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }
