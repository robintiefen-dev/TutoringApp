from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


# Create your models here.
class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.code


class TutoringHour(models.Model):
    ta = models.ForeignKey("TAProfile", on_delete=models.CASCADE)

    weekday = models.CharField(max_length=9, blank=True)
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def clean(self):
        super().clean()

        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError("End time must be later than start time.")

        if bool(self.weekday) == bool(self.date):
            raise ValidationError(
                "Provide either a weekday or a specific date, but not both."
            )


class TAProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    courses = models.ManyToManyField(Course, blank=True)

    def __str__(self):
        return self.user.username
