from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response

from .serializers import RegisterSerializer, EmailLoginSerializer, UserProfileSerializer

User = get_user_model()


# register new user
class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# login using email + password
class EmailLoginView(generics.GenericAPIView):
    serializer_class   = EmailLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # return tokens + user info
        return Response(serializer.validated_data)


# get/update logged-in user profile
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class   = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    # always return current logged-in user
    def get_object(self):
        return self.request.user