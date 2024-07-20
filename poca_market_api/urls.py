"""
URL configuration for poca_market_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="인플루디오 사전과제 API",
        default_version="v1",
        description="포카마켓 포토카드 서비스 구현 "
        "API 상세: https://docs.google.com/document/d/1_z_HPDLqwEG-SIxrQMuCnR4RlLGrlDZ0iOsS3IUefSQ/edit?usp=sharing",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(name="chaeyeonhan", email="gkscodus11@gmail.com"),
    ),
    public=True,
    permission_classes=(AllowAny,),
    authentication_classes=(),
)

api_url_patterns = [path("users/", include("user.urls")), path("photocards/", include("photocard.urls"))]

urlpatterns = [path("admin/", admin.site.urls), path("api/", include(api_url_patterns))]

urlpatterns += [  # DEBUG=True일때만 실행하는게 맞지만, 과제 테스트를 위해 False일때도 실행가능하도록 수정
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    re_path(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]


if settings.DEBUG:
    urlpatterns += [
        path("silk/", include("silk.urls")),
    ]
