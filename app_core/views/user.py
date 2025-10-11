
import logging
import random
import string
import threading
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import viewsets, status
from rest_framework.decorators import action

from app_core.middlewares.permissions import IsManager
from app_core.helpers.response import RestResponse
from app_core.helpers.send_html_email import send_html_template_email
from app_core.middlewares.authentication import UserAuthentication
from app_core.models.user import User, UserStatus, UserRole
from app_core.serializers.user import ChangePasswordSerializer, UpdateUserSerializer, UserSerializer, CreateUserSerializer
from app_core.helpers.paginator import CustomPageNumberPagination

class UserView(viewsets.ViewSet):
    authentication_classes = (UserAuthentication, )

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [IsManager()]
        return []

    @swagger_auto_schema(request_body=CreateUserSerializer)
    def create(self, request):
        try:
            logging.getLogger().info("UserView.create req=%s", request.data)
            validate = CreateUserSerializer(data=request.data)

            if not validate.is_valid():
                return RestResponse(validate.errors, status=status.HTTP_400_BAD_REQUEST, message="Vui lòng kiểm tra lại dữ liệu của bạn!").response
            
            validated_data = validate.validated_data
            
            if User.objects.filter(email=validated_data["email"]).exists():
                return RestResponse(status=status.HTTP_400_BAD_REQUEST, message="Email đã được sử dụng bởi một tài khoản khác!").response
            
            _password: str = validated_data.pop("password")

            user = User(**validated_data)
            user.set_password(_password)
            user.status = UserStatus.UNVERIFIED
            user.role = UserRole.EMPLOYEE
            user.save() 
                
            return RestResponse(message="Thành công!", status=status.HTTP_201_CREATED).response
        except Exception as e:
            logging.getLogger().exception("UserView.create exc=%s, req=%s", e, request.data)
            return RestResponse(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @swagger_auto_schema(
        responses={200: UserSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                name="role",
                in_="query",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                name="size",
                in_="query",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                name="page",
                in_="query",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ]
    )
    def list(self, request):
        try:
            logging.getLogger().info("UserView.list req=%s", request.query_params)
            users = User.objects.all().order_by("-created_at")
            role = request.query_params.get("role", None)

            if role:
                users = users.filter(role=role)

            paginator = CustomPageNumberPagination()
            users = paginator.paginate_queryset(users, request)

            serializer = UserSerializer(users, many=True)
            return RestResponse(status=status.HTTP_200_OK, data=paginator.get_paginated_data(serializer.data)).response
        except Exception as e:
            logging.getLogger().exception("UserView.list exc=%s, req=%s", e, request.query_params)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    def retrieve(self, request, pk=None):
        try:
            logging.getLogger().info("UserView.retrieve pk=%s, req=%s", pk, request.query_params)
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return RestResponse(status=status.HTTP_200_OK, data=serializer.data).response
        except User.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND).response
        except Exception as e:
            logging.getLogger().exception("UserView.retrieve exc=%s, pk=%s, req=%s", e, pk, request.query_params)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    @action(methods=['GET'], detail=False, url_path='me')
    def me(self, request):
        try:
            logging.getLogger().info("UserView.me")
            user = User.objects.get(pk=request.user.id)
            serializer = UserSerializer(user)
            return RestResponse(status=status.HTTP_200_OK, data=serializer.data).response
        except User.DoesNotExist:
            return RestResponse(status=status.HTTP_404_NOT_FOUND).response
        except Exception as e:
            logging.getLogger().exception("UserView.me exc=%s", e)
            return RestResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR).response

    def __generate_random_password(self, length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def __send_password_reset_email(self, user, new_password):
        def send_mail():
            try:
                send_html_template_email(
                    to=[user.email],
                    subject="[Learn Gauge] Password reset notification",
                    template_name="password_reset.html",
                    context={
                        "user_name": user.name,
                        "new_password": new_password
                    }
                )
            except Exception as e:
                logging.getLogger().exception("UserView.__send_password_reset_email exc=%s", e)

        thread = threading.Thread(target=send_mail)
        thread.daemon = True
        thread.start()
    
    @swagger_auto_schema(
        request_body=UpdateUserSerializer,
        responses={
            200: UserSerializer(),
            400: 'Bad Request',
            404: 'Not Found',
            500: 'Internal Server Error'
        }
    )
    def update(self, request, pk=None):
        try:
            logging.getLogger().info("UserView.update pk=%s, req=%s", pk, request.data)
            
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return RestResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    message="Không tìm thấy người dùng!"
                ).response
            
            serializer = UpdateUserSerializer(
                instance=user,
                data=request.data,
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return RestResponse(
                    data=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Vui lòng kiểm tra lại dữ liệu!"
                ).response
            
            updated_user = serializer.save()
            response_serializer = UserSerializer(updated_user, exclude=['password'])
            
            return RestResponse(
                data=response_serializer.data,
                status=status.HTTP_200_OK,
                message="Cập nhật thông tin thành công!"
            ).response
            
        except Exception as e:
            logging.getLogger().exception("UserView.update exc=%s, pk=%s, req=%s", e, pk, request.data)
            return RestResponse(
                data={"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).response

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            200: 'Success',
            400: 'Bad Request',
            500: 'Internal Server Error'
        }
    )
    @action(methods=['POST'], detail=False, url_path='me/change-password')
    def change_password(self, request):
        try:
            logging.getLogger().info("WebUserView.change_password user=%s", request.user.id)
            
            serializer = ChangePasswordSerializer(
                data=request.data,
                context={'user': request.user}
            )
            
            if not serializer.is_valid():
                return RestResponse(
                    data=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Vui lòng kiểm tra lại dữ liệu!"
                ).response
            
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save(update_fields=['password'])
            
            return RestResponse(
                status=status.HTTP_200_OK,
                message="Đổi mật khẩu thành công!"
            ).response
            
        except Exception as e:
            logging.getLogger().exception("WebUserView.change_password exc=%s, user=%s", e, request.user.id)
            return RestResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Lỗi khi đổi mật khẩu!"
            ).response 