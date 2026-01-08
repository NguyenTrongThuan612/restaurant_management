import logging
from datetime import date
from rest_framework import viewsets, status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser

from app_core.models.daily_quantity import DailyQuantity
from app_core.serializers.daily_quantity import (
    DailyQuantitySerializer,
    CreateDailyQuantitySerializer
)
from app_core.helpers.response import RestResponse
from app_core.helpers.paginator import CustomPageNumberPagination
from app_core.middlewares.authentication import UserAuthentication
from app_core.middlewares.permissions import IsManager

class DailyQuantityView(viewsets.ViewSet):
    parser_classes = (JSONParser,)
    authentication_classes = (UserAuthentication,)

    def get_permissions(self):
        if self.action in ['create']:
            return [IsManager()]
        return []

    @swagger_auto_schema(
        responses={200: DailyQuantitySerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(name="page", in_="query", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter(name="size", in_="query", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter(name="date", in_="query", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=False, description="Filter by date (YYYY-MM-DD)"),
            openapi.Parameter(name="dish_id", in_="query", type=openapi.TYPE_INTEGER, required=False, description="Filter by dish ID"),
            openapi.Parameter(name="combo_id", in_="query", type=openapi.TYPE_INTEGER, required=False, description="Filter by combo ID"),
        ]
    )
    def list(self, request):
        try:
            logging.getLogger().info("DailyQuantityView.list req=%s", request.query_params)
            queryset = DailyQuantity.objects.all()

            # Filter by date
            date_param = request.query_params.get('date')
            if date_param:
                try:
                    filter_date = date.fromisoformat(date_param)
                    queryset = queryset.filter(date=filter_date)
                except ValueError:
                    return RestResponse(
                        status=status.HTTP_400_BAD_REQUEST,
                        message="Invalid date format. Use YYYY-MM-DD format."
                    ).response

            # Filter by dish_id
            dish_id = request.query_params.get('dish_id')
            if dish_id:
                queryset = queryset.filter(dish_id=dish_id)

            # Filter by combo_id
            combo_id = request.query_params.get('combo_id')
            if combo_id:
                queryset = queryset.filter(combo_id=combo_id)

            serializer = DailyQuantitySerializer(queryset, many=True)
            paginator = CustomPageNumberPagination()
            queryset = paginator.paginate_queryset(queryset, request)

            return RestResponse(status=status.HTTP_200_OK, data=paginator.get_paginated_data(serializer.data)).response
        except Exception as e:
            logging.getLogger().exception("DailyQuantityView.list exc=%s, req=%s", e, request.query_params)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

    @swagger_auto_schema(request_body=CreateDailyQuantitySerializer)
    def create(self, request):
        try:
            logging.getLogger().info("DailyQuantityView.create req=%s", request.data)
            serializer = CreateDailyQuantitySerializer(data=request.data)

            if not serializer.is_valid():
                return RestResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    data=serializer.errors,
                    message="Vui lòng kiểm tra lại dữ liệu!"
                ).response

            # Upsert: Check if daily quantity already exists for this date and dish/combo
            date_value = serializer.validated_data['date']
            dish = serializer.validated_data.get('dish')
            combo = serializer.validated_data.get('combo')
            quantity = serializer.validated_data['quantity']

            # Try to get existing record
            if dish:
                obj, created = DailyQuantity.objects.get_or_create(
                    date=date_value,
                    dish=dish,
                    defaults={
                        'type': serializer.validated_data['type'],
                        'quantity': quantity
                    }
                )
                if not created:
                    # Update existing record
                    obj.quantity = quantity
                    obj.save()
            elif combo:
                obj, created = DailyQuantity.objects.get_or_create(
                    date=date_value,
                    combo=combo,
                    defaults={
                        'type': serializer.validated_data['type'],
                        'quantity': quantity
                    }
                )
                if not created:
                    # Update existing record
                    obj.quantity = quantity
                    obj.save()

            return RestResponse(status=status.HTTP_200_OK, data=DailyQuantitySerializer(obj).data).response
        except Exception as e:
            logging.getLogger().exception("DailyQuantityView.create exc=%s, req=%s", e, request.data)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)}).response

