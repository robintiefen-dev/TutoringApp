from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .models import TAProfile, TutoringHour
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TASignUpForm


# Create your views here.
def is_ta(user):
    return user.is_authenticated and TAProfile.objects.filter(user=user).exists()


@login_required
def ta_dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied
    ta = get_object_or_404(TAProfile, user=request.user)

    tutoring_hours = TutoringHour.objects.filter(ta=ta)

    return render(
        request,
        "tutoring/ta_dashboard.html",
        {
            "ta": ta,
            "tutoring_hours": tutoring_hours,
        },
    )

    return HttpResponse("TA Dashboard")


def ta_signup(request):
    if request.method == "POST":
        form = TASignUpForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = TASignUpForm()

    return render(request, "tutoring/signup.html", {"form": form})


def ta_detail(request, pk):
    ta = get_object_or_404(TAProfile, pk=pk)
    courses = ta.courses.all()

    return render(
        request,
        "tutoring/ta_detail.html",
        {
            "ta": ta,
            "courses": courses,
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
