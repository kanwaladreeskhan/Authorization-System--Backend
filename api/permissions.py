from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):

    def has_permission(
        self,
        request,
        view
    ):

        return (
            request.user.is_authenticated
            and
            request.user.groups.filter(
                name='Admin'
            ).exists()
        )


class IsUser(BasePermission):

    def has_permission(
        self,
        request,
        view
    ):

        return (
            request.user.is_authenticated
            and
            request.user.groups.filter(
                name='User'
            ).exists()
        )

from .models import ResourcePermission


class HasReportAccess(BasePermission):

    def has_permission(self, request, view):

        return ResourcePermission.objects.filter(
            user=request.user,
            resource__in=[
                "weekly_reports",
                "monthly_reports",
                "annual_reports",
                "financial_reports"
            ],
            can_view=True
        ).exists()
    
class IsAdult(
    BasePermission
):

    def has_permission(
        self,
        request,
        view
    ):

        return (
            request.user.age >= 18
        )