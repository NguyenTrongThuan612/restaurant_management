import logging
from datetime import datetime
from rest_framework import viewsets, status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from app_core.models.dining_table import DiningTable
from app_core.serializers.dining_table import DiningTableSerializer, CreateDiningTableSerializer, UpdateDiningTableSerializer
from app_core.helpers.response import RestResponse
from app_core.helpers.paginator import CustomPageNumberPagination
from app_core.middlewares.authentication import UserAuthentication
from app_core.middlewares.permissions import IsManager, IsEmployee

class DiningTableView(viewsets.ViewSet):
    authentication_classes = (UserAuthentication, )

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsManager()]
        return []
    
    @swagger_auto_schema(responses={200: DiningTableSerializer(many=True)}, manual_parameters=[
        openapi.Parameter(name="page", in_="query", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter(name="size", in_="query", type=openapi.TYPE_INTEGER, required=False),
    ])
    def list(self, request):
        try:
            logging.getLogger().info("DiningTableView.list req=%s", request.query_params)
            queryset = DiningTable.objects.filter(deleted_at=None)
            serializer = DiningTableSerializer(queryset, many=True)
            paginator = CustomPageNumberPagination()
            queryset = paginator.paginate_queryset(queryset, request)
            return RestResponse(status=status.HTTP_200_OK, data=paginator.get_paginated_data(serializer.data)).response
        except Exception as e:
            logging.getLogger().exception("DiningTableView.list exc=%s, req=%s", e, request.query_params)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(responses={200: DiningTableSerializer})
    def retrieve(self, request, pk=None):
        try:
            logging.getLogger().info("DiningTableView.retrieve pk=%s", pk)
            queryset = DiningTable.objects.get(pk=pk, deleted_at=None)
            serializer = DiningTableSerializer(queryset)
            return RestResponse(status=status.HTTP_200_OK, data=serializer.data).response
        except DiningTable.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy bàn ăn!").response
        except Exception as e:
            logging.getLogger().exception("DiningTableView.retrieve exc=%s, pk=%s", e, pk)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(request_body=CreateDiningTableSerializer)
    def create(self, request):
        try:
            logging.getLogger().info("DiningTableView.create req=%s", request.data)
            serializer = CreateDiningTableSerializer(data=request.data)

            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response
           
            if DiningTable.objects.filter(code=serializer.validated_data['code'], deleted_at=None).exists():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Mã bàn ăn đã tồn tại!").response

            obj = DiningTable(**serializer.validated_data)
            obj.save()
            return RestResponse(status=status.HTTP_200_OK, data=DiningTableSerializer(obj).data).response
        except Exception as e:
            logging.getLogger().exception("DiningTableView.create exc=%s, req=%s", e, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(request_body=UpdateDiningTableSerializer)
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("DiningTableView.update pk=%s, req=%s", pk, request.data)
            serializer = UpdateDiningTableSerializer(data=request.data)

            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response

            obj = DiningTable.objects.get(pk=pk, deleted_at=None)
            obj.update(**serializer.validated_data)
            return RestResponse(status=status.HTTP_200_OK, data=DiningTableSerializer(obj).data).response
        except DiningTable.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy bàn ăn!").response
        except Exception as e:
            logging.getLogger().exception("DiningTableView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    def destroy(self, request, pk=None):
        try:
            logging.getLogger().info("DiningTableView.destroy pk=%s", pk)
            obj = DiningTable.objects.get(pk=pk, deleted_at=None)
            obj.deleted_at = datetime.now()
            obj.save()
            return RestResponse(status=status.HTTP_200_OK, data=DiningTableSerializer(obj).data).response
        except DiningTable.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy bàn ăn!").response
        except Exception as e:
            logging.getLogger().exception("DiningTableView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response