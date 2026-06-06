# api/serializers.py
from rest_framework import serializers
from .models import CustomUser

from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "phone", "profile_image","role"]



