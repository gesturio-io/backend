# NOT STABLE , NOT USED 


from django.contrib.auth.backends import BaseBackend
from .models import UserAuth
from .utils import validate_token

# NOT STABLE , NOT USED 
class JWTAuthenticationBackend(BaseBackend):
    """Custom authentication backend for JWT token authentication."""

    def authenticate(self, request, jwt_token=None):
        
        """Authenticate user using JWT token."""
        
        if not jwt_token:
            return None
        
        payload = validate_token(jwt_token)
        
        if not payload:
            return None

        try:
            user = UserAuth.objects.get(user_id=payload["user_id"])
            return user
        
        except UserAuth.DoesNotExist:
            return None

    def get_user(self, user_id):
        
        """Retrieve user by user_id."""
        
        try:
            return UserAuth.objects.get(user_id=user_id)
        
        except UserAuth.DoesNotExist:
            return None
