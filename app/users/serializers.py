from rest_framework import serializers
from app.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "role",
            "created_at"
            "username",
            "password",
            "email",
        ]
        extra_kwargs = {
            "role": {"required": False, "default": "user"},
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "role",
            "username",
            "password",
            "email",
        ]
        extra_kwargs = {
            "role": {"required": False, "default": "user"},
            "username": {"required": False, "allow_blank": True, "allow_null": True},
        }

    def update(self, instance: User, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user



