from django.urls import include, path

from user.views import auth_views, profile_views

auth_url_patterns = [
    path("register/", auth_views.UserRegisterView.as_view(), name="user-register"),
    path("login/", auth_views.UserLoginView.as_view(), name="user-login"),
]

urlpatterns = [path("auth/", include(auth_url_patterns)), path("me/", profile_views.UserProfileView.as_view())]
