from django.http import JsonResponse
from django.core.cache import cache
import re
from django.conf import settings

PRIVATE_IP_REGEX = re.compile(
    r"^(10\.\d+\.\d+\.\d+)"  # 10.0.0.0 – 10.255.255.255
    r"|^(172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+)"  # 172.16.0.0 – 172.31.255.255
    r"|^(192\.168\.\d+\.\d+)"  # 192.168.0.0 – 192.168.255.255
    r"|^(127\.\d+\.\d+\.\d+)"  # 127.0.0.1 (localhost)
    r"|^(::1)"  # IPv6 localhost
    r"|^(fc00::/7)"  # IPv6 private range
    r"|^(fe80::/10)"  # Link-local IPv6
)

def is_private_ip(ip):
    """Checks if an IP address is private."""
    return bool(PRIVATE_IP_REGEX.match(ip))

def get_client_ip(request):
    """Extracts the real client IP address securely."""

    trusted_proxies = settings.TRUSTED_PROXIES

    remote_addr = request.META.get("REMOTE_ADDR")

    if remote_addr in trusted_proxies:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_list = [ip.strip() for ip in x_forwarded_for.split(",")]

            for ip in ip_list:
                if not is_private_ip(ip):
                    return ip  

    return remote_addr


