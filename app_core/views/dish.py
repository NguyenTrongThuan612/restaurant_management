import logging
from datetime import datetime
from rest_framework import viewsets, status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser

from app_core.models.dish import Dish
from app_core.serializers.dish import DishSerializer, CreateDishSerializer, UpdateDishSerializer
from app_core.helpers.response import RestResponse
from app_core.helpers.paginator import CustomPageNumberPagination
from app_core.middlewares.authentication import UserAuthentication
from app_core.middlewares.permissions import IsManager, IsEmployee

class DishView(viewsets.ViewSet):
    parser_classes = (MultiPartParser,)
    authentication_classes = (UserAuthentication, )

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsManager()]
        return []

    @swagger_auto_schema(
        responses={200: DishSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(name="page", in_="query", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter(name="size", in_="query", type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    def list(self, request):
        try:
            logging.getLogger().info("DishView.list req=%s", request.query_params)
            queryset = Dish.objects.filter(deleted_at=None)
            serializer = DishSerializer(queryset, many=True)
            paginator = CustomPageNumberPagination()
            queryset = paginator.paginate_queryset(queryset, request)

            return RestResponse(status=status.HTTP_200_OK, data=paginator.get_paginated_data(serializer.data)).response
        except Exception as e:
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(responses={200: DishSerializer})
    def retrieve(self, request, pk=None):
        try:
            logging.getLogger().info("DishView.retrieve pk=%s", pk)
            queryset = Dish.objects.get(pk=pk, deleted_at=None)
            serializer = DishSerializer(queryset)
            return RestResponse(status=status.HTTP_200_OK, data=serializer.data).response
        except Dish.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy món ăn!").response
        except Exception as e:
            logging.getLogger().exception("DishView.retrieve exc=%s, pk=%s", e, pk)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response
        
    @swagger_auto_schema(request_body=CreateDishSerializer)
    def create(self, request):
        try:
            logging.getLogger().info("DishView.create req=%s", request.data)
            serializer = CreateDishSerializer(data=request.data)

            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response

            obj = Dish(**serializer.validated_data)
            obj.save()

            return RestResponse(status=status.HTTP_200_OK, data=DishSerializer(obj).data).response
        except Exception as e:
            logging.getLogger().exception("DishView.create exc=%s, req=%s", e, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(request_body=UpdateDishSerializer)
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("DishView.update pk=%s, req=%s", pk, request.data)
            serializer = UpdateDishSerializer(data=request.data)

            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response

            obj = Dish.objects.get(pk=pk, deleted_at=None)
            obj.update(**serializer.validated_data)
            return RestResponse(status=status.HTTP_200_OK, data=DishSerializer(obj).data).response
        except Dish.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy món ăn!").response
        except Exception as e:
            logging.getLogger().exception("DishView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    def destroy(self, request, pk=None):
        try:
            logging.getLogger().info("DishView.destroy pk=%s", pk)
            obj = Dish.objects.get(pk=pk, deleted_at=None)
            obj.deleted_at = datetime.now()
            obj.save()
            return RestResponse(status=status.HTTP_200_OK, data=DishSerializer(obj).data).response
        except Dish.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy món ăn!").response
        except Exception as e:
            logging.getLogger().exception("DishView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response
