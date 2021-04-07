"""Viewsets for the User model"""

# Django
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_204_NO_CONTENT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

# Personal
from jklib.django.db.queries import get_object_or_none
from jklib.django.drf.permissions import (
    AllowAny,
    IsAdminUser,
    IsNotAuthenticated,
    IsObjectOwner,
)
from jklib.django.drf.serializers import IdListSerializer
from jklib.django.drf.viewsets import ImprovedModelViewSet, ImprovedViewSet

# Application
from core.permissions import IsNotVerified
from security.models import SecurityToken

# Local
from .models import User
from .serializers import (
    BaseUserAdminSerializer,
    BaseUserSerializer,
    PasswordResetSerializer,
    RequestPasswordResetSerializer,
    UpdatePasswordSerializer,
    UserAdminCreateSerializer,
    UserCreateSerializer,
    VerifySerializer,
)


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class UserAdminViewSet(ImprovedModelViewSet):
    """User API for admins"""

    queryset = User.objects.all()
    viewset_permissions = (IsAdminUser,)
    permission_classes = {"default": None}
    serializer_classes = {
        "default": BaseUserAdminSerializer,
        "bulk_destroy": IdListSerializer,
        "create": UserAdminCreateSerializer,
        "request_verification": None,
    }

    @action(detail=True, methods=["post"])
    def request_verification(self, request, pk=None):
        """Sends an email to the user for him to verify his account"""
        user = self.get_object()
        if user.is_verified:
            return Response(None, status=HTTP_422_UNPROCESSABLE_ENTITY)
        token_type, token_duration = User.VERIFY_TOKEN
        token = SecurityToken.create_new_token(user, token_type, token_duration)
        user.send_verification_email(token, async_=False)
        return Response(None, HTTP_204_NO_CONTENT)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    ImprovedViewSet,
):
    """User API for users"""

    queryset = User.objects.all()
    viewset_permissions = None
    permission_classes = {
        "default": (IsObjectOwner,),
        "create": (IsNotAuthenticated,),
        "request_password_reset": (IsNotAuthenticated,),
        "perform_password_reset": (IsNotAuthenticated,),
        "request_verification": (IsObjectOwner & IsNotVerified),
        "verify": (AllowAny,),
    }

    serializer_classes = {
        "default": BaseUserSerializer,
        "create": UserCreateSerializer,
        "perform_password_reset": PasswordResetSerializer,
        "request_password_reset": RequestPasswordResetSerializer,
        "request_verification": None,
        "update_password": UpdatePasswordSerializer,
        "verify": VerifySerializer,
    }

    def create(self, request, *args, **kwargs):
        """Overridden to send the user an email"""
        serializer = self.get_valid_serializer(data=request.data)
        user = serializer.save()
        if not user.is_verified:
            token_type, token_duration = User.VERIFY_TOKEN
            token = SecurityToken.create_new_token(user, token_type, token_duration)
            user.send_verification_email(token, async_=True)
        else:
            user.send_welcome_email(async_=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=["post"])
    def perform_password_reset(self, request):
        """Resets the user password if the token is valid"""
        serializer = self.get_valid_serializer(data=request.data)
        user = serializer.save()
        user.send_password_updated_email(async_=True)
        return Response(None, HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def request_password_reset(self, request):
        """Creates a token and ends the reset email to the user matching the provided email"""
        serializer = self.get_valid_serializer(data=request.data)
        email = serializer.validated_data["email"]
        user = get_object_or_none(User, email=email)
        if user is not None:
            token_type, token_duration = User.RESET_TOKEN
            token = SecurityToken.create_new_token(user, token_type, token_duration)
            user.send_reset_password_email(token, async_=True)
        return Response(None, HTTP_202_ACCEPTED)

    @action(detail=True, methods=["post"])
    def request_verification(self, request, pk=None):
        """Creates a token and sends the verification email to our user"""
        user = self.get_object()
        if user.is_verified:
            return Response(None, status=HTTP_422_UNPROCESSABLE_ENTITY)
        token_type, token_duration = User.VERIFY_TOKEN
        token = SecurityToken.create_new_token(user, token_type, token_duration)
        user.send_verification_email(token, async_=False)
        return Response(None, HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["put"])
    def update_password(self, request, pk=None):
        """Updates our user's current password"""
        user = self.get_object()
        serializer = self.get_valid_serializer(user, data=request.data)
        user = serializer.save()
        user.send_password_updated_email(async_=True)
        return Response(None, HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def verify(self, request):
        """Flags the user linked to the token as verified"""
        serializer = self.get_valid_serializer(data=request.data)
        user, has_changed = serializer.save()
        if has_changed:
            user.send_welcome_email(async_=True)
        return Response(None, HTTP_204_NO_CONTENT)
