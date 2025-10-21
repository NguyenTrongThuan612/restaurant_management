from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from app_core.views.health import HealthCheckView
from app_core.views.user import UserView
from app_core.views.auth import AuthView
from app_core.views.dish import DishView
from app_core.views.combo import ComboView
from app_core.views.dining_table import DiningTableView
from app_core.views.order import OrderView
from app_core.views.order_item import OrderItemView
from app_core.views.bill import BillView
from app_core.views.statistical import StatisticalView

router = DefaultRouter(trailing_slash=False)
router.register('users', UserView, basename='user')
router.register('auth', AuthView, basename='auth')
router.register('dishes', DishView, basename='dish')
router.register('combos', ComboView, basename='combo')
router.register('dining-tables', DiningTableView, basename='dining-table')
router.register('orders', OrderView, basename='order')
router.register('order-items', OrderItemView, basename='order-item')
router.register('bills', BillView, basename='bill')
router.register('statistical', StatisticalView, basename='statistical')

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('', include(router.urls)),
]