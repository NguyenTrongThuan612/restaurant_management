import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction

from app_core.models.order import Order, OrderStatus
from app_core.models.bill import Bill
from app_core.serializers.bill import BillSerializer, CreateBillSerializer
from app_core.helpers.response import RestResponse
from app_core.middlewares.authentication import UserAuthentication
from app_core.helpers.paginator import CustomPageNumberPagination

class BillView(viewsets.ViewSet):
    authentication_classes = (UserAuthentication, )

    def retrieve(self, request, pk=None):
        try:
            logging.getLogger().info("BillView.retrieve pk=%s", pk)
            queryset = Bill.objects.get(pk=pk)
            serializer = BillSerializer(queryset)
            return RestResponse(status=status.HTTP_200_OK, data=serializer.data).response
        except Bill.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy hóa đơn!").response
        except Exception as e:
            logging.getLogger().exception("BillView.retrieve exc=%s, pk=%s", e, pk)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(name="page", in_="query", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter(name="size", in_="query", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter(name="order", in_="query", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter(name="created_at", in_="query", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter(name="created_by", in_="query", type=openapi.TYPE_INTEGER, required=False),
    ])
    def list(self, request):
        try:
            logging.getLogger().info("BillView.list req=%s", request.query_params)
            queryset = Bill.objects.all()

            order = request.query_params.get("order", None)
            if order:
                queryset = queryset.filter(order=order)

            created_at = request.query_params.get("created_at", None)
            if created_at:
                queryset = queryset.filter(created_at__date=created_at)

            created_by = request.query_params.get("created_by", None)
            if created_by:
                queryset = queryset.filter(created_by=created_by)

            serializer = BillSerializer(queryset, many=True)
            paginator = CustomPageNumberPagination()
            queryset = paginator.paginate_queryset(queryset, request)
            return RestResponse(status=status.HTTP_200_OK, data=paginator.get_paginated_data(serializer.data)).response
        except Exception as e:
            logging.getLogger().exception("BillView.list exc=%s, req=%s", e, request.query_params)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response


    @swagger_auto_schema(request_body=CreateBillSerializer)
    def create(self, request):
        try:
            logging.getLogger().info("BillView.create req=%s", request.data)
            serializer = CreateBillSerializer(data=request.data)

            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response

            order = Order.objects.get(id=serializer.validated_data['order'])

            if order.status != OrderStatus.PENDING:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Đơn đặt bàn đã được xử lý!").response

            if order.employee != request.user:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Bạn không có quyền tạo hóa đơn cho đơn đặt bàn này!").response

            total_amount = sum(item.price * item.quantity for item in order.order_items.all())
            
            with transaction.atomic():
                bill = Bill.objects.create(order=order, total_amount=total_amount, created_by=request.user)
                order.status = OrderStatus.COMPLETED
                order.save()

            return RestResponse(status=status.HTTP_200_OK, data=BillSerializer(bill).data).response
        except Exception as e:
            logging.getLogger().exception("BillView.create exc=%s, req=%s", e, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response
                
                