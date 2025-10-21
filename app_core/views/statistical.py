import logging
from rest_framework import viewsets, status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from collections import defaultdict
from rest_framework.decorators import action

from app_core.middlewares.authentication import UserAuthentication
from app_core.middlewares.permissions import IsManager
from app_core.helpers.response import RestResponse
from app_core.models.bill import Bill
from app_core.models.order_item import OrderItem, OrderItemType
from app_core.models.order import Order

class StatisticalView(viewsets.ViewSet):
    authentication_classes = (UserAuthentication, )
    permission_classes = (IsManager, )

    @action(detail=False, methods=['GET'], url_path='revenue')
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(name="start_date", in_="query", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter(name="end_date", in_="query", type=openapi.TYPE_STRING, required=True),
    ])
    def revenue(self, request):
        try:
            logging.getLogger().info("StatisticalView.revenue req=%s", request.query_params)
            start_date_str = request.query_params.get("start_date", None)
            end_date_str = request.query_params.get("end_date", None)

            if not start_date_str or not end_date_str:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Ngày bắt đầu và ngày kết thúc là bắt buộc!").response

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

            if start_date > end_date:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc!").response

            queryset = Bill.objects.filter(created_at__date__range=[start_date, end_date])
            total_revenue = queryset.aggregate(total_revenue=Sum('total_amount'))['total_revenue']
            revenue_by_date = queryset.values('created_at__date').annotate(total_revenue=Sum('total_amount')).annotate(date=F('created_at__date'))
            bill_by_date = queryset.values('created_at__date').annotate(number_of_bills=Count('id')).annotate(date=F('created_at__date'))
            data = {
                "revenue_by_date": revenue_by_date,
                "bill_by_date": bill_by_date,
                "total_revenue": total_revenue,
                "number_of_bills": queryset.count(),
                "number_of_days": (end_date - start_date).days + 1,
                "from": start_date_str,
                "to": end_date_str,
            }
            return RestResponse(status=status.HTTP_200_OK, data=data).response
        except ValueError:
            return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Ngày bắt đầu và ngày kết thúc phải là định dạng yyyy-mm-dd!").response
        except Exception as e:
            logging.getLogger().exception("StatisticalView.revenue exc=%s, req=%s", e, request.query_params)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @action(detail=False, methods=['GET'], url_path='dish-and-combo-sold')
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(name="start_date", in_="query", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter(name="end_date", in_="query", type=openapi.TYPE_STRING, required=True),
    ])
    def dish_and_combo_sold(self, request):
        try:
            logging.getLogger().info("StatisticalView.dish_and_combo_sold req=%s", request.query_params)
            start_date_str = request.query_params.get("start_date", None)
            end_date_str = request.query_params.get("end_date", None)

            if not start_date_str or not end_date_str:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Ngày bắt đầu và ngày kết thúc là bắt buộc!").response

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start_date > end_date:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc!").response

            bills = Bill.objects.filter(created_at__date__range=[start_date, end_date])
            order_items = OrderItem.objects.filter(order__bills__in=bills)

            dish_qs = (
                order_items.filter(type=OrderItemType.DISH)
                .annotate(date=TruncDate('order__bills__created_at'))
                .values('date', 'dish__id', 'dish__name')
                .annotate(total_quantity=Sum('quantity'))
                .order_by('-date', '-total_quantity')
            )

            combo_qs = (
                order_items.filter(type=OrderItemType.COMBO)
                .annotate(date=TruncDate('order__bills__created_at'))
                .values('date', 'combo__id', 'combo__name')
                .annotate(total_quantity=Sum('quantity'))
                .order_by('-date', '-total_quantity')
            )

            grouped_by_date = defaultdict(lambda: {"dishes": [], "combos": []})
            for r in dish_qs:
                grouped_by_date[r['date']]["dishes"].append({
                    "dish_id": r['dish__id'],
                    "dish_name": r['dish__name'],
                    "total_quantity": r['total_quantity'],
                })
            for r in combo_qs:
                grouped_by_date[r['date']]["combos"].append({
                    "combo_id": r['combo__id'],
                    "combo_name": r['combo__name'],
                    "total_quantity": r['total_quantity'],
                })

            by_date = []
            for d in sorted(grouped_by_date.keys(), reverse=True):
                by_date.append({
                    "date": d,
                    "dishes": grouped_by_date[d]["dishes"],
                    "combos": grouped_by_date[d]["combos"],
                })

            top_5_dishes = (
                order_items.filter(type=OrderItemType.DISH)
                .values('dish__id', 'dish__name')
                .annotate(total_quantity=Sum('quantity'))
                .order_by('-total_quantity')[:5]
            )
            top_5_dishes = [{"dish_id": r["dish__id"], "dish_name": r["dish__name"], "total_quantity": r["total_quantity"]} for r in top_5_dishes]

            top_5_combos = (
                order_items.filter(type=OrderItemType.COMBO)
                .values('combo__id', 'combo__name')
                .annotate(total_quantity=Sum('quantity'))
                .order_by('-total_quantity')[:5]
            )
            top_5_combos = [{"combo_id": r["combo__id"], "combo_name": r["combo__name"], "total_quantity": r["total_quantity"]} for r in top_5_combos]

            data = {
                "by_date": by_date,
                "top_5_dishes": top_5_dishes,
                "top_5_combos": top_5_combos,
            }
            return RestResponse(status=status.HTTP_200_OK, data=data, message="Thành công!").response

        except Exception as e:
            logging.getLogger().exception("StatisticalView.dish_and_combo_sold exc=%s, req=%s", e, request.query_params)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @action(detail=False, methods=['GET'], url_path='employee-performance')
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(name="start_date", in_="query", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter(name="end_date", in_="query", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter(name="employee", in_="query", type=openapi.TYPE_INTEGER, required=False),
    ])
    def employee_performance(self, request):
        try:
            logging.getLogger().info("StatisticalView.employee_performance req=%s", request.query_params)
            start_date_str = request.query_params.get("start_date", None)
            end_date_str = request.query_params.get("end_date", None)

            if not start_date_str or not end_date_str:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Ngày bắt đầu và ngày kết thúc là bắt buộc!"
                ).response

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            employee_id = request.query_params.get("employee", None)

            if start_date > end_date:
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc!"
                ).response

            bills = Bill.objects.filter(created_at__date__range=[start_date, end_date])

            if employee_id:
                bills = bills.filter(created_by__id=employee_id)

            bills_by_employee = (
                bills.values('created_by__id', 'created_by__fullname')
                .annotate(number_of_bills=Count('id'))
                .order_by('-number_of_bills')
            )

            orders_by_employee = (
                Order.objects.filter(bills__in=bills)
                .values('employee__id', 'employee__fullname')
                .annotate(number_of_orders=Count('id'))
                .order_by('-number_of_orders')
            )

            bills_per_date_qs = (
                bills.annotate(date=TruncDate('created_at'))
                .values('date', 'created_by__id', 'created_by__fullname')
                .annotate(number_of_bills=Count('id'))
                .order_by('-date')
            )

            orders_per_date_qs = (
                Order.objects.filter(bills__in=bills)
                .annotate(date=TruncDate('created_at'))
                .values('date', 'employee__id', 'employee__fullname')
                .annotate(number_of_orders=Count('id'))
                .order_by('-date')
            )

            bills_grouped = defaultdict(list)
            for r in bills_per_date_qs:
                bills_grouped[r['date']].append({
                    "employee_id": r['created_by__id'],
                    "employee_name": r['created_by__fullname'],
                    "number_of_bills": r['number_of_bills'],
                })

            orders_grouped = defaultdict(list)
            for r in orders_per_date_qs:
                orders_grouped[r['date']].append({
                    "employee_id": r['employee__id'],
                    "employee_name": r['employee__fullname'],
                    "number_of_orders": r['number_of_orders'],
                })

            bills_by_employee_per_date = [
                {"date": d, "employees": bills_grouped[d]} for d in sorted(bills_grouped.keys(), reverse=True)
            ]

            orders_by_employee_per_date = [
                {"date": d, "employees": orders_grouped[d]} for d in sorted(orders_grouped.keys(), reverse=True)
            ]

            data = {
                "bills_by_employee": bills_by_employee,
                "orders_by_employee": orders_by_employee,
                "bills_by_employee_per_date": bills_by_employee_per_date,
                "orders_by_employee_per_date": orders_by_employee_per_date,
            }
            return RestResponse(status=status.HTTP_200_OK, data=data).response

        except Exception as e:
            logging.getLogger().exception("StatisticalView.employee_performance exc=%s, req=%s", e, request.query_params)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={"error": str(e)}
            ).response