from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .models import TAProfile, TutoringHour, Course
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TASignUpForm, TutoringHourForm
from django.db import transaction


# Create your views here.
def is_ta(user):
    return user.is_authenticated and TAProfile.objects.filter(user=user).exists()


@login_required
def ta_dashboard(request):
    if not is_ta(request.user):
        raise PermissionDenied

    ta = get_object_or_404(TAProfile, user=request.user)

    if request.method == "POST":
        form = TutoringHourForm(request.POST)

        if form.is_valid():
            hour = form.save(commit=False)
            hour.ta = ta
            hour.save()
            return redirect("ta_dashboard")
    else:
        form = TutoringHourForm()

    tutoring_hours = TutoringHour.objects.filter(ta=ta)

    return render(
        request,
        "tutoring/ta_dashboard.html",
        {
            "ta": ta,
            "tutoring_hours": tutoring_hours,
            "form": form,
        },
    )


def ta_signup(request):
    if request.method == "POST":
        form = TASignUpForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()

                ta = TAProfile.objects.create(user=user)

                ta.courses.set(form.cleaned_data["courses"])

                day = form.cleaned_data.get("tutoring_day")
                start = form.cleaned_data.get("tutoring_start")
                end = form.cleaned_data.get("tutoring_end")

                if day and start and end:
                    TutoringHour.objects.create(
                        ta=ta,
                        weekday=day,
                        start_time=start,
                        end_time=end,
                    )

            return redirect("login")
    else:
        form = TASignUpForm()

    return render(
        request,
        "tutoring/signup.html",
        {"form": form},
    )


def ta_detail(request, pk):
    ta = get_object_or_404(TAProfile, pk=pk)
    courses = ta.courses.all()

    tutoring_hours = TutoringHour.objects.filter(ta=ta).order_by("start_time")

    return render(
        request,
        "tutoring/ta_detail.html",
        {
            "ta": ta,
            "courses": courses,
            "tutoring_hours": tutoring_hours,
        },
    )


def home(request):
    tas = TAProfile.objects.all()
    tutoring_hours = TutoringHour.objects.select_related("ta", "ta__user").all()

    return render(
        request,
        "tutoring/home.html",
        {
            "tas": tas,
            "tutoring_hours": tutoring_hours,
        },
    )


@login_required
def staff_dashboard(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    tas = TAProfile.objects.filter(user__is_active=True).prefetch_related("courses")

    courses = Course.objects.all()

    tutoring_hours = TutoringHour.objects.count()

    return render(
        request,
        "tutoring/staff_dashboard.html",
        {
            "tas": tas,
            "courses": courses,
            "tutoring_hours": tutoring_hours,
        },
    )


@login_required
def delete_tutoring_hour(request, pk):
    if not is_ta(request.user):
        raise PermissionDenied

    hour = get_object_or_404(TutoringHour, pk=pk, ta__user=request.user)

    if request.method == "POST":
        hour.delete()
        return redirect("ta_dashboard")

    raise PermissionDenied


@login_required
def edit_tutoring_hour(request, pk):
    if not is_ta(request.user):
        raise PermissionDenied

    hour = get_object_or_404(
        TutoringHour,
        pk=pk,
        ta__user=request.user,
    )

    if request.method == "POST":
        form = TutoringHourForm(request.POST, instance=hour)

        if form.is_valid():
            form.save()
            return redirect("ta_dashboard")
    else:
        form = TutoringHourForm(instance=hour)

    return render(
        request,
        "tutoring/edit_tutoring_hour.html",
        {"form": form, "hour": hour},
    )
