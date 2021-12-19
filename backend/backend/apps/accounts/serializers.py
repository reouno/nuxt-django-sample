"""account serializers"""
from datetime import date

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models.models import CustomUser


class NativeLoginSerializer(serializers.Serializer):
    """Login serializer"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def create(self, validated_data):
        """No need to implement"""
        raise NotImplementedError()

    def update(self, instance, validated_data):
        """No need to implement"""
        raise NotImplementedError()


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""

    class Meta:
        """Meta"""
        model = CustomUser
        exclude = ('password',)

    def validate_birthday(self, value):
        """birthday field validation"""
        if value > date.today():
            raise serializers.ValidationError('You are not born yet.')

        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        """password validation"""
        validate_password(value)
        return value

    def create(self, validated_data):
        """No need to implement"""
        raise NotImplementedError()

    def update(self, instance, validated_data):
        """No need to implement"""
        raise NotImplementedError()


def validate_first_name(value):
    """first_name validation"""
    if value is None:
        raise serializers.ValidationError('This field is required.')
    if len(value) == 0 or len(value) > 64:
        raise serializers.ValidationError(
            'This field must not be empty and must have no more than 64 characters.'
        )

    return value


class CreateUserSerializer(serializers.Serializer):
    """Signup request serializer"""
    first_name = serializers.CharField(validators=[validate_first_name])
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(required=True, validators=[validate_password])

    def create(self, validated_data):
        """No need to implement"""
        raise NotImplementedError()

    def update(self, instance, validated_data):
        """No need to implement"""
        raise NotImplementedError()


class ProvisionalUserSerializer(serializers.Serializer):
    """Serializer for provisional registration
    Email field validation is not required because if the signup link will not be reached to the
    user if the email is invalid.
    """
    email = serializers.EmailField(required=True)

    def create(self, validated_data):
        """No need to implement"""
        raise NotImplementedError()

    def update(self, instance, validated_data):
        """No need to implement"""
        raise NotImplementedError()
