import logging
from datetime import datetime
from django.db import transaction
from rest_framework import viewsets, status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action

from app_core.middlewares.authentication import UserAuthentication
from app_core.serializers.order import (
    OrderSerializer, 
    UpdateOrderSerializer, 
    CreateOrderSerializer, 
    CreateOrderItemSerializer, 
    UpdateOrderItemSerializer
)
from app_core.models.order import Order, OrderStatus
from app_core.models.order_item import OrderItem
from app_core.helpers.paginator import CustomPageNumberPagination
from app_core.helpers.response import RestResponse

class OrderView(viewsets.ViewSet):
    authentication_classes = (UserAuthentication, )

    @swagger_auto_schema(responses={200: OrderSerializer(many=True)}, manual_parameters=[
        openapi.Parameter(name="page", in_="query", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter(name="size", in_="query", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter(name="status", in_="query", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter(name="customer_name", in_="query", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter(name="customer_phone", in_="query", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter(name="dining_table", in_="query", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter(name="employee", in_="query", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter(name="date", in_="query", type=openapi.TYPE_STRING, required=False),
    ])
    def list(self, request):
        try:
            logging.getLogger().info("OrderView.list req=%s", request.query_params)
            queryset = Order.objects.filter()

            status_f = request.query_params.get("status", None)
            if status_f:
                queryset = queryset.filter(status=status_f)

            customer_name = request.query_params.get("customer_name", None)
            if customer_name:
                queryset = queryset.filter(customer_name__icontains=customer_name)

            customer_phone = request.query_params.get("customer_phone", None)
            if customer_phone:
                queryset = queryset.filter(customer_phone=customer_phone)

            dining_table = request.query_params.get("dining_table", None)
            if dining_table:
                queryset = queryset.filter(dining_table=dining_table)

            employee = request.query_params.get("employee", None)
            if employee:
                queryset = queryset.filter(employee=employee)

            date = request.query_params.get("date", None)
            if date:
                queryset = queryset.filter(created_at__date=date)

            serializer = OrderSerializer(queryset, many=True)
            paginator = CustomPageNumberPagination()
            queryset = paginator.paginate_queryset(queryset, request)
            return RestResponse(status=status.HTTP_200_OK, data=paginator.get_paginated_data(serializer.data)).response
        except Exception as e:
            logging.getLogger().exception("OrderView.list exc=%s, req=%s", e, request.query_params)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(responses={200: OrderSerializer})
    def retrieve(self, request, pk=None):
        try:
            logging.getLogger().info("OrderView.retrieve pk=%s", pk)
            queryset = Order.objects.get(pk=pk)
            serializer = OrderSerializer(queryset)
            return RestResponse(status=status.HTTP_200_OK, data=serializer.data).response
        except Order.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy đơn đặt bàn!").response
        except Exception as e:
            logging.getLogger().exception("OrderView.retrieve exc=%s, pk=%s", e, pk)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(responses={200: OrderSerializer}, request_body=CreateOrderSerializer)
    def create(self, request):
        try:
            logging.getLogger().info("OrderView.create req=%s", request.data)
            serializer = CreateOrderSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response
            with transaction.atomic():
                order = Order(**serializer.validated_data)
                order.save()

                for item in serializer.validated_data['order_items']:
                    OrderItem(**item, order=order).save()

            return RestResponse(status=status.HTTP_200_OK, data=OrderSerializer(order).data).response
        except Exception as e:
            logging.getLogger().exception("OrderView.create exc=%s, req=%s", e, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(request_body=UpdateOrderSerializer)
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("OrderView.update pk=%s, req=%s", pk, request.data)
            serializer = UpdateOrderSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response

            queryset = Order.objects.get(pk=pk)
            for key, value in serializer.validated_data.items():
                setattr(queryset, key, value)
            queryset.save()

            return RestResponse(status=status.HTTP_200_OK).response
        except Order.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy đơn đặt bàn!").response
        except Exception as e:
            logging.getLogger().exception("OrderView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @action(detail=True, methods=['PATCH'], url_path='cancel')
    def cancel(self, request, pk=None):
        try:
            logging.getLogger().info("OrderView.cancel pk=%s", pk)
            queryset = Order.objects.get(pk=pk)

            if queryset.status != OrderStatus.PENDING:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Không thể hủy đơn đặt bàn!").response

            queryset.status = OrderStatus.CANCELLED
            queryset.save()
            return RestResponse(status=status.HTTP_200_OK).response
        except Order.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy đơn đặt bàn!").response
        except Exception as e:
            logging.getLogger().exception("OrderView.cancel exc=%s, pk=%s", e, pk)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @action(detail=True, methods=['DELETE'], url_path='order-items/(?P<pk_order_item>\d+)')
    def delete_order_item(self, request, pk=None, pk_order_item=None):
        try:
            logging.getLogger().info("OrderView.delete_order_item pk=%s, pk_order_item=%s", pk, pk_order_item)
            order = Order.objects.get(pk=pk)

            if order.status != OrderStatus.PENDING:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Không thể xóa sản phẩm khỏi đơn đặt bàn đã hoàn thành!").response

            queryset = OrderItem.objects.get(pk=pk_order_item, deleted_at=None)

            if queryset.order.id != order.id:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Sản phẩm không thuộc đơn đặt bàn!").response

            queryset.deleted_at = datetime.now()
            queryset.save()
            return RestResponse(status=status.HTTP_200_OK).response
        except Order.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy đơn đặt bàn!").response
        except OrderItem.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy sản phẩm!").response
        except Exception as e:
            logging.getLogger().exception("OrderView.delete_order_item exc=%s, pk=%s, pk_order_item=%s", e, pk, pk_order_item)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @action(detail=True, methods=['POST'], url_path='order-items')
    def add_order_item(self, request, pk=None):
        try:
            logging.getLogger().info("OrderView.add_order_item pk=%s, req=%s", pk, request.data)
            serializer = CreateOrderItemSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response

            order = Order.objects.get(pk=pk)
            if order.status != OrderStatus.PENDING:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Không thể thêm sản phẩm vào đơn đặt bàn đã hoàn thành!").response

            OrderItem.objects.create(
                order=order,
                **serializer.validated_data
            )
            return RestResponse(status=status.HTTP_200_OK).response
        except Order.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy đơn đặt bàn!").response
        except Exception as e:
            logging.getLogger().exception("OrderView.add_order_item exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(request_body=UpdateOrderItemSerializer)
    @action(detail=True, methods=['PUT'], url_path='order-items/(?P<pk_order_item>\d+)')
    def update_order_item(self, request, pk=None, pk_order_item=None):
        try:
            logging.getLogger().info("OrderView.update_order_item pk=%s, pk_order_item=%s", pk, pk_order_item)
            serializer = UpdateOrderItemSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response

            order = Order.objects.get(pk=pk)
            if order.status != OrderStatus.PENDING:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Không thể cập nhật sản phẩm của đơn đặt bàn đã hoàn thành!").response

            queryset = OrderItem.objects.get(pk=pk_order_item, deleted_at=None)
            if queryset.order.id != order.id:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Sản phẩm không thuộc đơn đặt bàn!").response

            for key, value in serializer.validated_data.items():
                setattr(queryset, key, value)
            queryset.save()
            return RestResponse(status=status.HTTP_200_OK).response
        except Order.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy đơn đặt bàn!").response
        except OrderItem.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy sản phẩm!").response
        except Exception as e:
            logging.getLogger().exception("OrderView.update_order_item exc=%s, pk=%s, pk_order_item=%s", e, pk, pk_order_item)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response