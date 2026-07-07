from django.utils import timezone
from datetime import timedelta
from .throttles import (
    LoginThrottle,
    RegisterThrottle,
    RefreshThrottle
)
from .permissions import (
    IsAdmin,
    IsUser,
    HasReportAccess,
    IsAdult
)
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import (
    RefreshToken as JWTRefreshToken
)

from .permissions import (
    IsAdmin,
    IsUser
)
from .models import User, RefreshToken
from .serializers import (
    RegisterSerializer,
    LoginSerializer
)
from .utils import hash_token

from rest_framework.permissions import AllowAny

 

class RegisterView(APIView):

    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]
    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "message":
                    "User registered successfully"
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):

    permission_classes = [AllowAny]
    authentication_classes=[]
    throttle_classes = [LoginThrottle]
    def post(self,request):

        print("HEADERS")
        print(request.headers)

        serializer=LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )
        user = serializer.validated_data['user']

        refresh = JWTRefreshToken.for_user(user)

        # Save refresh token hash in DB
        RefreshToken.objects.create(
            user=user,
            token_hash=hash_token(
                str(refresh)
            ),
            expires_at=(
                timezone.now()
                + timedelta(days=7)
            )
        )

        response = Response({

    "access_token":
        str(
            refresh.access_token
        ),

    "user": {

        "id":
            user.id,

        "email":
            user.email,

        "full_name":
            user.full_name,

        "role":
            (
                user.groups
                .first()
                .name
                if user.groups.exists()
                else None
            )
    }
})

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False,   # True in production
            samesite='Lax'
        )

        return response


class RefreshView(APIView):

    permission_classes = [AllowAny]
    throttle_classes = [RefreshThrottle]
    def post(self, request):

        refresh_token = (
    request.data.get('refresh_token')
    or
    request.COOKIES.get('refresh_token')
)

        if not refresh_token:
            return Response(
                {
                    "error":
                    "Refresh token missing"
                },
                status=401
            )

        try:

            refresh = JWTRefreshToken(
                refresh_token
            )

            user_id = refresh['user_id']

            user = User.objects.get(
                id=user_id
            )
            
            # Generate new refresh token
            new_refresh = (
                JWTRefreshToken.for_user(
                    user
                )
            )

            # Generate new access token
            access = str(
                new_refresh.access_token
            )

            # Find old token in DB
            old_token = (
                RefreshToken.objects.get(
                    token_hash=hash_token(
                        refresh_token
                    )
                )
            )
               # Detect refresh token reuse attack
            if old_token.revoked_at:

                # revoke entire token family
                RefreshToken.objects.filter(
                family_id=old_token.family_id,
                revoked_at__isnull=True
                 ).update(
                revoked_at=timezone.now()
                 )

                return Response(
                 {
            "error":
            "Refresh token reuse detected. Entire session revoked."
                },
                status=401
    )
            # Revoke old token
            old_token.revoked_at = (
                timezone.now()
            )

            old_token.replaced_by = (
                hash_token(
                    str(new_refresh)
                )
            )

            old_token.save()

            # Save new token
            RefreshToken.objects.create(
                user=user,
                token_hash=hash_token(
                    str(new_refresh)
                ),
                family_id=old_token.family_id,
                expires_at=(
                    timezone.now()
                    + timedelta(days=7)
                )
            )

            # Blacklist old JWT token
            #refresh.blacklist()

            response = Response({
                "access_token":
                    access
            })

            response.set_cookie(
                key='refresh_token',
                value=str(new_refresh),
                httponly=True,
                secure=False,
                samesite='Lax'
            )

            return response

        except Exception as e:

            print("ERROR:", type(e))
            print("MESSAGE:", str(e))

            return Response(
                {
                    "error": str(e)
                },
                status=401
            )
        



class AdminDashboardView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin
    ]

    def get(self, request):

        return Response({

            "message":
                "Welcome Admin",

            "email":
                request.user.email
        })


class UserDashboardView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsUser
    ]

    def get(self, request):

        return Response({

            "message":
                "Welcome User",

            "email":
                request.user.email
        })

class DashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        if user.groups.filter(
            name='Admin'
        ).exists():

            return Response({

                "redirect":
                    "/admin-dashboard",

                "role":
                    "Admin"
            })

        if user.groups.filter(
            name='User'
        ).exists():

            return Response({

                "redirect":
                    "/user-dashboard",

                "role":
                    "User"
            })

        return Response({

            "message":
                "No role assigned"
        })
    




class ReportsView(
    APIView
):

    permission_classes = [

        IsAuthenticated,
        HasReportAccess
    ]

    def get(
        self,
        request
    ):

        return Response({

            "message":
                "ACL Success"
        })
    
class AdultContentView(
    APIView
):

    permission_classes = [

        IsAuthenticated,
        IsAdult
    ]

    def get(
        self,
        request
    ):

        return Response({

            "message":
                "ABAC Success"
        })


from .models import ResourcePermission

class MyPermissionsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        permissions = ResourcePermission.objects.filter(
            user=request.user
        )

        data = []

        for p in permissions:
            data.append({
                "resource": p.resource,
                "can_view": p.can_view,
                "can_edit": p.can_edit
            })

        return Response(data)
    
class AssignReportAccessView(
    APIView
):

    permission_classes = [
        IsAuthenticated,
        IsAdmin
    ]

    def post(
        self,
        request
    ):

        email = request.data.get(
            "email"
        )

        permissions = request.data.get(
            "permissions",
            {}
        )

        user = User.objects.filter(
            email=email
        ).first()

        if not user:

            return Response(
                {
                    "error":
                    "User not found"
                },
                status=404
            )

        ALLOWED_RESOURCES = [

            "weekly_reports",
            "monthly_reports",
            "annual_reports",
            "financial_reports"
        ]

        for resource, allowed in permissions.items():

            if resource not in ALLOWED_RESOURCES:
                continue

            permission, _ = (
                ResourcePermission.objects
                .get_or_create(
                    user=user,
                    resource=resource
                )
            )

            permission.can_view = allowed

            permission.save()

        return Response({

            "message":
            "Permissions updated successfully"
        })

class LogoutView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        response = Response({
            "message": "Logged out"
        })

        response.delete_cookie("refresh_token")

        return response
    
