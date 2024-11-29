from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from .models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    @extend_schema_field(serializers.CharField(help_text='Unique identifier'))
    def get_username(self, obj):
        return obj.username

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type']

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserMinimalSerializer(read_only=True)
    receiver = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'sender', 'receiver', 'message', 'topic', 'is_read', 'can_be_sent']
        

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_at'] = instance.created_at.isoformat()
        return representation


class LeaveRequestSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = ['id', 'user', 'start_date', 'end_date', 'reason', 'status']
        read_only_fields = ['status']  # Status should be 'pending' by default


class HourlyLeaveRequestSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

    class Meta:
        model = HourlyLeaveRequest
        fields = ['id', 'user', 'start_time', 'end_time', 'reason', 'status']
        read_only_fields = ['status']  # Status should be 'pending' by default


class LateToWorkMinutesSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    class Meta:
        model = LateToWorkMinutes
        fields = ['id', 'user', 'late_to_work_minutes', 'is_logined', 'is_full_day']