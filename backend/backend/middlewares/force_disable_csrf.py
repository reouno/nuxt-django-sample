"""Force disable CSRF checks"""
from django.utils.deprecation import MiddlewareMixin


# FIXME: カスタムヘッダー付与できない問題が解決したらこのミドルウェアを削除する
# refs: https://github.com/aitit-inc/q-it/issues/232
class ForceDisableCsrf(MiddlewareMixin):
    """Middleware to force disable CSRF checks"""

    def process_request(self, request):
        """Set not to check CSRF when processing request"""
        setattr(request, '_dont_enforce_csrf_checks', True)
