from django.urls import path, include
from rest_framework.routers import SimpleRouter

from app_core.views.health import HealthCheckView
from app_core.views.user import UserView
from app_core.views.auth import AuthView
from app_core.views.dish import DishView
from app_core.views.combo import ComboView
from app_core.views.dining_table import DiningTableView
from app_core.views.order import OrderView

router = SimpleRouter(trailing_slash=False)

router.register('users', UserView, basename='user')
router.register('auth', AuthView, basename='auth')
router.register('dishes', DishView, basename='dish')
router.register('combos', ComboView, basename='combo')
router.register('dining-tables', DiningTableView, basename='dining-table')
router.register('orders', OrderView, basename='order')

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('', include(router.urls)),
]