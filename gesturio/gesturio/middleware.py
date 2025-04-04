import time
import hashlib
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from .utility import get_client_ip
from django.utils.deprecation import MiddlewareMixin
from users.backends import JWTAuthenticationBackend

# NOT STABLE , NOT USED 
class JWTAuthenticationMiddleware(MiddlewareMixin):
    
    """Middleware to authenticate users using JWT tokens."""

    def process_request(self, request):
    
        """Check JWT token and authenticate user before processing request."""
    
        token = request.COOKIES.get("jwt")
        if token:
            auth_backend = JWTAuthenticationBackend()
            user = auth_backend.authenticate(request, jwt_token=token)
            if user:
                request.user = user
            else:
                request.user = None


class RateLimiterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.default_rate_limit = settings.RATE_LIMIT_DEFAULT
        self.default_window = settings.RATE_LIMIT_WINDOW


    def __call__(self, request):

        if request.method not in ['GET', 'POST']:
            return self.get_response(request)

        client_id = self.client_identifier(request)

        rate_limit, window = self.limit_settings(request.path)

        if not self.check_rate_limit(client_id, rate_limit, window):
            response = JsonResponse({'error': 'Too Many Requests'}, status=429)
            response['X-RateLimit-Limit'] = str(rate_limit)
            response['X-RateLimit-Remaining'] = '0'
            response['X-RateLimit-Reset'] = str(int(time.time()) + window)
            return response

        response = self.get_response(request)

        remaining = self.remaining_requests(client_id, rate_limit, window)
        response['X-RateLimit-Limit'] = str(rate_limit)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(int(time.time()) + window)
        
        return response

    # CAUSES PROBLEMS WHILE USING A PROXY
    # def client_identifier(self, request):
    #     """Generate a unique identifier for the client using IP, User-Agent, and optional authentication data."""
        
    #     ip = get_client_ip(request)
    #     print(ip)
    #     user_agent = request.META.get('HTTP_USER_AGENT', '')
    #     accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    #     accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        
    #     if not hasattr(request, 'user'):
    #         return hashlib.sha256(f"{ip}|{user_agent}|{accept_language}|{accept_encoding}".encode()).hexdigest()
        
    #     user_id = getattr(request.user, 'user_id', None)  # Use user_id if logged in    

    #     unique_string = f"{user_id or ip}|{user_agent}|{accept_language}|{accept_encoding}"
    #     return hashlib.sha256(unique_string.encode()).hexdigest()
    
    
    def client_identifier(self, request):
        """Generate a unique identifier for rate limiting."""
        
        ip = get_client_ip(request)
        # print(ip)
        # user_agent = request.META.get("HTTP_USER_AGENT", "")
        
        if not hasattr(request, 'user'):
            return hashlib.sha256(f"{ip}".encode()).hexdigest()
        
        user_id = getattr(request.user, "user_id", None)

        # Generate a unique key combining IP, User-Agent, and user ID (if available)
        unique_string = f"{user_id}|{ip}"
        return hashlib.sha256(unique_string.encode()).hexdigest()



    def limit_settings(self, path: str):
        """Get rate limit settings per API path."""
        custom_limits = {
            '/api/v1/auth/': (10, 60),  
            '/api/v1/data/': (50, 60),
            '/accounts/get-ip/':(5,60),
            '/accounts/logout/':(5,60),
        }
        return custom_limits.get(path, (self.default_rate_limit, self.default_window))


    def check_rate_limit(self, client_id: str, rate_limit: int, window: int):
    
        """Check if the client exceeded the rate limit."""
    
        cache_key = f'rateLimit:{client_id}'
        current = cache.get(cache_key, 0)

        if current >= rate_limit:
            return False

        cache.set(cache_key, current + 1, window)
        return True


    def remaining_requests(self, client_id: str, rate_limit: int, window: int):
        """Get remaining requests for the client."""
        cache_key = f'rateLimit:{client_id}'
        current = cache.get(cache_key, 0)
        return max(0, rate_limit - current)
