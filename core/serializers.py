from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import ValidationError, AuthenticationFailed, NotAuthenticated

from core.models import User

USER_MODEL = get_user_model()


class PasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs['style'] = {'input_type': 'password'}
        kwargs.setdefault('write_only', True)
        super().__init__(**kwargs)
        self.validators.append(validate_password)


class RegistrationSerializer(serializers.ModelSerializer):
    password = PasswordField(required=True)
    password_repeat = PasswordField(required=True)

    class Meta:
        model = USER_MODEL
        read_only_fields = ('id',)
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_repeat']:
            raise ValidationError('Passwords are different.')
        return attrs

    def create(self, validated_data):
        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = USER_MODEL
        fields = ('username', 'password')

    def create(self, validated_data):
        if not (user := authenticate(username=validated_data['username'], password=validated_data['password'])):
            raise AuthenticationFailed
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER_MODEL
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UpdatePasswordSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = USER_MODEL
        fields = ('old_password', 'new_password', 'user')

    def validate(self, attrs):
        if not (user := attrs['user']):
            raise NotAuthenticated
        if not user.check_password(attrs['old_password']):
            raise ValidationError('Incorrect old password.')
        return attrs

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance: User, validated_data):
        instance.password = make_password(validated_data['new_password'])
        instance.save(update_fields=('password',))
        return instance
