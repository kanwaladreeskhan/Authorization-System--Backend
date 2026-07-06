import email

from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group

class RegisterSerializer(
    serializers.ModelSerializer
):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    role = serializers.CharField(
        write_only=True,
        required=False,
        default='User'
    )

    class Meta:

        model = User

        fields = [
            'email',
            'username',
            'full_name',
            'password',
            'role'
        ]

    def create(
        self,
        validated_data
    ):

        role = validated_data.pop(
            'role',
            'User'
        )

        password = validated_data.pop(
            'password'
        )

        user = User(
            **validated_data
        )

        user.set_password(
            password
        )

        user.save()

        group, _ = (
            Group.objects
            .get_or_create(
                name=role
            )
        )

        user.groups.add(
            group
        )

        return user

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        email = attrs.get('email')
        password = attrs.get('password')

        print("\n====================")
        print("EMAIL:", email)
        print("PASSWORD:", password)

        

        user = User.objects.filter(email=email).first()

        print("USER:", user)

        if user:
            print(
        "CHECK:",
        user.check_password(password)
    )

        print("AUTH USER:", user)
        print("====================\n")

        if not user:
            raise serializers.ValidationError(
                "Invalid credentials"
            )

        attrs['user'] = user

        return attrs    


 
from rest_framework_simplejwt.tokens import (
    RefreshToken as JWTRefreshToken
)


class RefreshSerializer(serializers.Serializer):

    refresh_token = serializers.CharField()

    def validate(self, attrs):

        try:
            refresh = JWTRefreshToken(
                attrs['refresh_token']
            )

            attrs['refresh'] = refresh

            return attrs

        except Exception:

            raise serializers.ValidationError(
                "Invalid refresh token"
            )

