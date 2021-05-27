from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.response import Response
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from drf_yasg import openapi

from .models import Classes, Users, FileStore
from .serializer import (ClassSerializer, LoginSerializer,
                         StudentFilterSerializer, UserSerializer, FileSerializer)
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, FileUploadParser
import test
import os
import facenetv2

class StudentAPIView(generics.GenericAPIView):
    @swagger_auto_schema(request_body=StudentFilterSerializer)
    def post(self, request):
        class_id = request.data['class_id']

        students = Users.objects.filter(
            details_student_attend_class__course__pk=class_id)

        if 'filter_options' in request.data:
            filter_options = request.data['filter_options']
            if 'gender' in filter_options:
                students = students.filter(gender=filter_options['gender'])

            if 'full_name' in filter_options:
                students = students.filter(
                    full_name=filter_options['full_name'])

            if 'email' in filter_options:
                students = students.filter(email=filter_options['email'])

            if 'student_id' in filter_options:
                students = students.filter(user_id=filter_options['student_id'])

            if 'birthday' in filter_options:
                students = students.filter(birthday=filter_options['birthday'])

        serializer = UserSerializer(students, many=True)
        return Response(serializer.data)


class ClassAPIView(generics.GenericAPIView):
    def get(self, request):
        classes = Classes.objects.all()
        serializer = ClassSerializer(classes, many=True)
        return Response(serializer.data)


class LoginAPIView(generics.GenericAPIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]
        try:
            user = Users.objects.get(email=email)

            if user.password == password:
                serializer = UserSerializer(user)
                return Response(serializer.data)
            return HttpResponse('Password incorrect.', status=401)
        except ObjectDoesNotExist:
            return HttpResponse("User doesn't exist", status=401)

class RecognizeAPIView(generics.CreateAPIView):
    serializer_class = FileSerializer
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, *args, **kwargs):
        file_data = request.data.get('file', None)
        new_file = FileStore.objects.create(file=file_data)

        current_path = str(os.path.abspath(os.getcwd())) # .../AISrc
        img_path = current_path + "\img" + "\\" +str(new_file.file)[4:]
        recog_api = test.Recog_Module()
        recoged_faces = recog_api.Recog_Process(img_path)
        return Response(recoged_faces)

class TrainFaceNetForNewPerSonAPIView(generics.GenericAPIView):
    new_person_name_param = openapi.Parameter('new_person_name', in_=openapi.IN_QUERY,type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[new_person_name_param])
    def post(self, request):
        name = request.query_params["new_person_name"]
        face_net = facenetv2.FaceNet()
        face_net.export_new_feature(name)
        return Response("thành công!")