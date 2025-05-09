from textwrap import dedent

from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Profile, User, Onboarding, Contraceptive
from .permissions import UserPermission
from .serializers import (
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    UserSerializer,
    OnboardingSerializer,
    ContraceptiveSerializer,
)


class UserModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        model = self.serializer_class.Meta.model
        # schema generation see https://drf-spectacular.readthedocs.io/en/latest/faq.html#my-get-queryset-depends-on-some-attributes-not-available-at-schema-generation-time
        if getattr(self, "swagger_fake_view", False):  # drf-yasg comp
            return model.objects.none()

        return model.objects.filter(user=self.request.user).order_by("-pk")


class UserCreateView(CreateAPIView):
    """Endpoint for creating a new User"""

    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserListView(ListAPIView):
    """Endpoint for listing all Users"""

    queryset = User.objects.all().order_by("email")
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserView(RetrieveAPIView, UpdateModelMixin, DestroyModelMixin):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, UserPermission]

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


@extend_schema_view(
    post=extend_schema(
        summary="Authentication endpoint returning a JWT",
        responses=TokenObtainPairSerializer,
    )
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    retrieve=extend_schema(summary="Retrieve profile by user-id"),
    partial_update=extend_schema(
        summary="Update profile by user-id",
        description=dedent(
            """\
            PATCH allows partial updates, so it is possible to only provide some of the keywords.
            - **language** should be an IETF lang code, the default is **de**.
            - **onboarding_finished** should be used to determine the onboarding status of a user.
              It is automatically set to true when a POST for the user is send
              to `/api/users/onboarding`.

            All profile settings are optional. To remove only the contraceptive
            for example, you can send the following json:

            ```json
            {"contraceptive": null}
            ```

            The string fields **first_name**, **last_name** and **language** are not nullable and trying
            to do so will return 400 Bad Request. If necessary, they can be set to an empty string:

            ```json
            {
              "first_name": "",
              "last_name": ""
            }
            ```
            """
        ),
    ),
)
class ProfileViewSet(viewsets.ModelViewSet):
    """
    The user profile contains most of the user information, apart from the login credentials.
    {user} is the id of the corresponding user.

    To delete a Profile, delete the corresponding [user](https://www.youtube.com/watch?v=dQw4w9WgXcQ).
    """

    queryset = Profile.objects.all().order_by("pk")
    serializer_class = ProfileSerializer
    http_method_names = ["get", "patch"]
    permission_classes = [IsAuthenticated, UserPermission]


class OnboardingViewSet(viewsets.ModelViewSet):
    """
    Onboarding data that is separate from the user profile, as it is only used during the initial months.
    As more data becomes available, rolling averages should be used instead of the initial estimates.
    """

    queryset = Onboarding.objects.all()
    serializer_class = OnboardingSerializer
    http_method_names = ["get", "post", "patch"]


@extend_schema_view(
    list=extend_schema(summary="List known contraceptive keywords"),
)
class ContraceptiveViewSet(viewsets.ModelViewSet):
    """
    Contraceptive keywords that are saved in the profile.
    """

    queryset = Contraceptive.objects.all().order_by("pk")
    serializer_class = ContraceptiveSerializer
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
