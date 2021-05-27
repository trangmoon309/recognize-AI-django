from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.urls import path
from . import views
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

schema_view = get_schema_view(
    openapi.Info(
        title="Student Management API",
        default_version='v1',
        description="Document for API",
        terms_of_service="https://www.pbl5.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny, ),
)

urlpatterns = [
    path('login', views.LoginAPIView.as_view()),
    path('students', views.StudentAPIView.as_view()),
    path('classes', views.ClassAPIView.as_view()),
    path('recognizes', views.RecognizeAPIView.as_view()),
    path('training-facenets', views.TrainFaceNetForNewPerSonAPIView.as_view()),

    path('doc',
         schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/',
         schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]
