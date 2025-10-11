import logging
from rest_framework import viewsets, status
from datetime import datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.decorators import action

from app_core.models.dish import Dish
from app_core.models.combo import Combo
from app_core.models.combo_dish import ComboDish
from app_core.serializers.combo import (
    ComboSerializer,
    CreateComboSerializer,
    UpdateComboSerializer,
    AddDishToComboSerializer,
    UpdateDishQuantityInComboSerializer
)
from app_core.helpers.response import RestResponse
from app_core.helpers.paginator import CustomPageNumberPagination
from app_core.middlewares.authentication import UserAuthentication
from app_core.middlewares.permissions import IsManager, IsEmployee

class ComboView(viewsets.ViewSet):
    parser_classes = (MultiPartParser,)
    authentication_classes = (UserAuthentication, )

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy', 'add_dish', 'update_dish', 'delete_dish']:
            return [IsManager()]
        return []

    @swagger_auto_schema(responses={200: ComboSerializer(many=True)}, manual_parameters=[
        openapi.Parameter(name="page", in_="query", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter(name="size", in_="query", type=openapi.TYPE_INTEGER, required=False),
    ])
    def list(self, request):
        try:
            logging.getLogger().info("ComboView.list req=%s", request.query_params)
            queryset = Combo.objects.filter(deleted_at=None)
            serializer = ComboSerializer(queryset, many=True)
            paginator = CustomPageNumberPagination()
            queryset = paginator.paginate_queryset(queryset, request)
            return RestResponse(status=status.HTTP_200_OK, data=paginator.get_paginated_data(serializer.data)).response
        except Exception as e:
            logging.getLogger().exception("ComboView.list exc=%s, req=%s", e, request.query_params)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(responses={200: ComboSerializer})
    def retrieve(self, request, pk=None):
        try:
            logging.getLogger().info("ComboView.retrieve pk=%s", pk)
            queryset = Combo.objects.get(pk=pk, deleted_at=None)
            serializer = ComboSerializer(queryset)
            return RestResponse(status=status.HTTP_200_OK, data=serializer.data).response
        except Combo.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy combo!").response
        except Exception as e:
            logging.getLogger().exception("ComboView.retrieve exc=%s, pk=%s", e, pk)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(request_body=CreateComboSerializer)
    def create(self, request):
        try:
            logging.getLogger().info("ComboView.create req=%s", request.data)
            serializer = CreateComboSerializer(data=request.data)

            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response

            obj = Combo(**serializer.validated_data)
            obj.save()
            return RestResponse(status=status.HTTP_200_OK, data=ComboSerializer(obj).data).response
        except Exception as e:
            logging.getLogger().exception("ComboView.create exc=%s, req=%s", e, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(request_body=UpdateComboSerializer)
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("ComboView.update pk=%s, req=%s", pk, request.data)
            serializer = UpdateComboSerializer(data=request.data)
            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response

            obj = Combo.objects.get(pk=pk, deleted_at=None)
            for key, value in serializer.validated_data.items():
                setattr(obj, key, value)
            obj.save()
            return RestResponse(status=status.HTTP_200_OK, data=ComboSerializer(obj).data).response
        except Combo.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy combo!").response
        except Exception as e:
            logging.getLogger().exception("ComboView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    def destroy(self, request, pk=None):
        try:
            logging.getLogger().info("ComboView.destroy pk=%s", pk)
            obj = Combo.objects.get(pk=pk, deleted_at=None)
            obj.deleted_at = datetime.now()
            obj.save()
            return RestResponse(status=status.HTTP_200_OK, data=ComboSerializer(obj).data).response
        except Combo.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy combo!").response
        except Exception as e:
            logging.getLogger().exception("ComboView.destroy exc=%s, pk=%s", e, pk)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @action(detail=True, methods=['POST'], parser_classes=(JSONParser, ), url_path='dish')
    @swagger_auto_schema(request_body=AddDishToComboSerializer)
    def add_dish(self, request, pk=None):
        try:
            logging.getLogger().info("ComboView.add_dish pk=%s, req=%s", pk, request.data)
            obj : Combo = Combo.objects.get(pk=pk, deleted_at=None)
            serializer = AddDishToComboSerializer(data=request.data)

            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response
            
            if obj.dishes.filter(dish=serializer.validated_data['dish'], deleted_at=None).exists():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Món ăn đã tồn tại trong combo!").response

            ComboDish.objects.create(
                combo=obj,
                dish=serializer.validated_data['dish'],
                quantity=serializer.validated_data['quantity']
            )
            return RestResponse(status=status.HTTP_200_OK, data=ComboSerializer(obj).data).response
        except Combo.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy combo!").response
        except Exception as e:
            logging.getLogger().exception("ComboView.add_dish exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @action(detail=True, methods=['PUT'], parser_classes=(JSONParser, ), url_path='dish/(?P<pk_dish>\d+)')
    @swagger_auto_schema(request_body=UpdateDishQuantityInComboSerializer)
    def update_dish(self, request, pk=None, pk_dish=None):
        try:
            logging.getLogger().info("ComboView.update_dish pk=%s, req=%s", pk, request.data)
            obj : Combo = Combo.objects.get(pk=pk, deleted_at=None)
            serializer = UpdateDishQuantityInComboSerializer(data=request.data)

            if not serializer.is_valid():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors, message="Vui lòng kiểm tra lại dữ liệu!").response

            if not obj.dishes.filter(dish=pk_dish, deleted_at=None).exists():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Món ăn không tồn tại trong combo!").response

            obj.dishes.filter(dish=pk_dish, deleted_at=None).update(quantity=serializer.validated_data['quantity'])
            return RestResponse(status=status.HTTP_200_OK, data=ComboSerializer(obj).data).response
        except Combo.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy combo!").response
        except Exception as e:
            logging.getLogger().exception("ComboView.update_dish exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @action(detail=True, methods=['DELETE'], parser_classes=(JSONParser, ), url_path='dish/(?P<pk_dish>\d+)')
    def delete_dish(self, request, pk=None, pk_dish=None):
        try:
            logging.getLogger().info("ComboView.delete_dish pk=%s, req=%s", pk, request.data)
            combo : Combo = Combo.objects.get(pk=pk, deleted_at=None)
            dish : Dish = Dish.objects.get(pk=pk_dish, deleted_at=None)
            combo.dishes.filter(dish=dish, deleted_at=None).delete()
            return RestResponse(status=status.HTTP_200_OK, data=ComboSerializer(combo).data).response
        except Dish.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy món ăn!").response
        except Combo.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND, message="Không tìm thấy combo!").response
        except Exception as e:
            logging.getLogger().exception("ComboView.delete_dish exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response
