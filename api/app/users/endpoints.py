from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import register
from django.contrib.auth import get_user_model
from users.permissions import IsOwnUser
from users.views import UserViewSet

@register
class UserEndpoint(Endpoint):
    url='auth/users'
    permission_classes = (IsOwnUser,)
    model = get_user_model()
    base_viewset = UserViewSet
    fields = (
            'username', 
            'first_name',
            'last_name',
            'email',
            'groups',
            'user_permissions'
        )