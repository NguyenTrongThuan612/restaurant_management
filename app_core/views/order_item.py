import logging
from datetime import datetime
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action

from app_core.middlewares.authentication import UserAuthentication
from app_core.serializers.order import (
    CreateOrderItemSerializer, 
    UpdateOrderItemSerializer
)
from app_core.models.order import Order, OrderStatus
from app_core.models.order_item import OrderItem
from app_core.helpers.response import RestResponse

class OrderItemView(viewsets.ViewSet):
    authentication_classes = (UserAuthentication, )

    @swagger_auto_schema(request_body=CreateOrderItemSerializer)
    def create(self, request):
        try:
            logging.getLogger().info("OrderItemView.create req=%s", request.data)
            serializer = CreateOrderItemSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response

            OrderItem.objects.create(
                **serializer.validated_data
            )
            return RestResponse(status=status.HTTP_200_OK).response
        except Exception as e:
            logging.getLogger().exception("OrderItemView.create exc=%s, req=%s", e, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(request_body=UpdateOrderItemSerializer)
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("OrderItemView.update pk=%s", pk)
            serializer = UpdateOrderItemSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response
            
            queryset = OrderItem.objects.get(pk=pk, deleted_at=None)

            if queryset.order.status != OrderStatus.PENDING:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Không thể cập nhật sản phẩm của đơn đặt bàn đã hoàn thành!").response

            for key, value in serializer.validated_data.items():
                setattr(queryset, key, value)
            queryset.save()
            return RestResponse(status=status.HTTP_200_OK).response
        except OrderItem.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy sản phẩm!").response
        except Exception as e:
            logging.getLogger().exception("OrderItemView.update exc=%s, pk=%s", e, pk)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    def destroy(self, request, pk=None):
        try:
            logging.getLogger().info("OrderItemView.destroy pk=%s", pk)
            queryset = OrderItem.objects.get(pk=pk, deleted_at=None)

            if queryset.order.status != OrderStatus.PENDING:
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Không thể xóa sản phẩm khỏi đơn đặt bàn đã hoàn thành!").response

            queryset.deleted_at = datetime.now()
            queryset.save()
            return RestResponse(status=status.HTTP_200_OK).response
        except OrderItem.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy sản phẩm!").response
        except Exception as e:
            logging.getLogger().exception("OrderItemView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response