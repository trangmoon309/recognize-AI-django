from django.core.files.base import File
from rest_framework import serializers
from rest_framework.fields import ImageField

from .models import Classes, Subjects, Users, FileStore


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=125)


class StudentFilterSerializer(serializers.Serializer):
    class FilterPayloadSerializer(serializers.Serializer):
        birthday = serializers.DateField()
        gender = serializers.CharField(max_length=10)
        email = serializers.CharField(max_length=255)
        student_id = serializers.IntegerField()
        full_name = serializers.CharField(max_length=255)

    class_id = serializers.IntegerField()
    filter_options = FilterPayloadSerializer(read_only=True)


class UserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    full_name = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)
    user_type = serializers.CharField(max_length=50)
    gender = serializers.CharField(max_length=10)
    birthday = serializers.DateField()


class SubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(max_length=50)

    class Meta:
        model = Subjects
        fields = ('subject_id', 'subject_name')


class ClassSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Classes
        fields = ('class_id', 'subject', 'teacher')


class FileSerializer(serializers.ModelSerializer):
    file = serializers.ImageField()
    class Meta:
        model = FileStore
        fields = ('__all__')