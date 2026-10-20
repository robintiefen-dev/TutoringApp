from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.ta_dashboard, name="ta_dashboard"),
    path("signup/", views.ta_signup, name="ta_signup"),
    path("ta/<int:pk>/", views.ta_detail, name="ta_detail"),
    path("", views.home, name="home"),
    path("staff-dashboard/", views.staff_dashboard, name="staff_dashboard"),
]
