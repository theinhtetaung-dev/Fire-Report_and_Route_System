from django.contrib.auth.backends import BaseBackend
from django.db.models import Q
from .models import User

class RoleAuthBackend(BaseBackend):
    """
    Custom authentication backend integrating DataAccess.models.User
    with Django's built-in session, authentication, and permission system.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        # Allow authentication via username OR email
        user = User.objects.select_related('role').filter(
            Q(username__iexact=username) | Q(email__iexact=username)
        ).first()

        if user and user.is_active and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.select_related('role').get(pk=user_id)
        except User.DoesNotExist:
            return None
