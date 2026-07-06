from django.urls import path

from .views import (
    AssignReportAccessView,
    RegisterView,
    LoginView,
    RefreshView,
    AdminDashboardView,
    UserDashboardView,
    DashboardView,
    ReportsView,
    AdultContentView,
    MyPermissionsView,
)

urlpatterns = [

    path(
        'register/',
        RegisterView.as_view()
    ),

    path(
        'login/',
        LoginView.as_view()
    ),
    path(
    'refresh/',
    RefreshView.as_view()
),
    path(
    'admin-dashboard/',
    AdminDashboardView.as_view()
),

path(
    'user-dashboard/',
    UserDashboardView.as_view()
),
path(
    'dashboard/',
    DashboardView.as_view()
),
path(
    'reports/',
    ReportsView.as_view()
),
path(
    'adult-content/',
    AdultContentView.as_view()
),
path(
    "my-permissions/",
    MyPermissionsView.as_view()
),
path(
    'assign-report-access/',
    AssignReportAccessView.as_view()
),
]