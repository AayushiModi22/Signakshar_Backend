from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('mainapp.urls')),
    # path('auth/api/login/google/', GoogleLoginApi.as_view(), name="GoogleLoginApi"),

]