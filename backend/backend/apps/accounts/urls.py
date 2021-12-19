"""account urls"""
from django.urls import path, re_path

from . import views
from .apps import AccountsConfig

app_name = AccountsConfig.name


def security_routes(url_path: str) -> str:
    """add `security/` prefix to the given path"""
    return 'security/' + url_path


urlpatterns = [
    path('empty-dict-204/', views.empty_dict_response_with_204, name='empty-dict-204'),
    path('empty-204/', views.just_empty_response_with_204, name='empty-204'),
    path('empty-dict-200/', views.empty_dict_response_with_200, name='empty-dict-200'),
    path('empty-200/', views.just_empty_response_with_200, name='empty-200'),

    path('set-csrf/', views.set_csrf_token, name='Set-Csrf'),
    path('login/', views.Login.as_view(), name='Login'),
    path('logout/', views.Logout.as_view(), name='Logout'),
    path('detail/', views.UserViews.as_view(), name='user'),

    # security routes
    path(security_routes('password/change/'), views.ChangePassword.as_view(),
         name='change-password'),
    path(security_routes('email/change/'), views.ChangeEmailAddress.as_view(), name='change-email'),

    # signup
    path('register_email/', views.ProvisionalSignup.as_view(), name='register_email'),
    re_path(r'^proceed_signup/(?P<uuid4>[0-9A-Za-z\-]+)/$', views.ProceedSignup.as_view(),
            name='proceed_signup'),
    path('signup/', views.Signup.as_view(), name='signup'),

    # debug
    path('debuglog/', views.DebugLogView.as_view(), name='debug_log'),
]
