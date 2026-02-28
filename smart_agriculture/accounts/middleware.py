"""
Role-based Access Control Middleware
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve


class RoleBasedAccessMiddleware:
    """
    Middleware to enforce role-based access control
    """
    
    # URL patterns accessible by each role
    ROLE_URL_PATTERNS = {
        'farmer': [
            '/farmer/',
            '/accounts/profile',
            '/accounts/logout',
            '/api/',
            '/soil/',
            '/weather/',
        ],
        'buyer': [
            '/buyer/',
            '/accounts/profile',
            '/accounts/logout',
            '/api/',
        ],
        'admin': [
            '/admin/',
            '/accounts/',
            '/api/',
            '/analytics/',
            '/farmer/',
            '/buyer/',
        ],
        'analyst': [
            '/analytics/',
            '/accounts/profile',
            '/accounts/logout',
            '/api/',
        ],
    }
    
    # Public URLs that don't require authentication
    PUBLIC_URLS = [
        '/',
        '/about/',
        '/accounts/login/',
        '/accounts/register/',
        '/accounts/password-reset/',
        '/static/',
        '/media/',
        '/admin/login/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if URL is public
        if self._is_public_url(request.path):
            return self.get_response(request)
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Check role-based access
        if not self._has_access(request.user, request.path):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core_dashboard:dashboard')
        
        return self.get_response(request)
    
    def _is_public_url(self, path):
        """Check if URL is publicly accessible"""
        for url in self.PUBLIC_URLS:
            if path.startswith(url):
                return True
        return False
    
    def _has_access(self, user, path):
        """Check if user has access to the given path"""
        user_role = user.role
        allowed_patterns = self.ROLE_URL_PATTERNS.get(user_role, [])
        
        for pattern in allowed_patterns:
            if path.startswith(pattern):
                return True
        
        # Allow access to dashboard
        if path.startswith('/dashboard/'):
            return True
        
        return False
