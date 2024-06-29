from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mainapp.myviews.user_views import JWTAuthentication
from mainapp.models import ApiLog
from mainapp.serializers import ApiLogSerializer

class ApiLogViewset(viewsets.ModelViewSet):
    queryset = ApiLog.objects.all()
    serializer_class = ApiLogSerializer

    def get_queryset(self):
        user = self.request.user
        return ApiLog.objects.filter(loggedin_user_id=user)

    def create(self, request, *args, **kwargs):
        log_level = request.data.get('log_level')
        loggedin_user_id = request.data.get('loggedin_user_id')

        # existing_log = ApiLog.objects.filter(
        #     log_level=log_level, loggedin_user_id=loggedin_user_id
        # ).exists()

        # if existing_log:
        #     return Response(
        #         {"error": "Log with the same level already exists for this user."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        return super().create(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method == 'POST':
            return []
        else:
            return [IsAuthenticated()]

    def get_authenticators(self):
        if self.request.method == 'POST':
            return []
        else:
            return [JWTAuthentication()]
