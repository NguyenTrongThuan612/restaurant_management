from django.urls import path, include
from rest_framework.routers import SimpleRouter

from app_core.views.health import HealthCheckView
from app_core.views.user import UserView
from app_core.views.auth import AuthView

router = SimpleRouter(trailing_slash=False)

router.register('users', UserView, basename='user')
router.register('auth', AuthView, basename='auth')

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('', include(router.urls)),
]