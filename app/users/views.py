from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from drf_spectacular.utils import extend_schema, OpenApiParameter

from app.models import User
from .serializers import UserSerializer, UserCreateUpdateSerializer


class CreateUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Users'],
        request=UserCreateUpdateSerializer,
        responses=UserSerializer,
    )
    def post(self, request):
        """
        Создать пользователя
        """
        serializer = UserCreateUpdateSerializer(data=request.data)

        if serializer.is_valid():
            created_user = serializer.save()

            return Response(UserSerializer(created_user).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Users'],
        parameters=[OpenApiParameter(
            name='user id',
            description='id пользователя для поиска',
            type=int,
            required=True,
        )],
        responses=UserSerializer,
    )
    def get(self, request):
        """
        Получить пользователя
        """
        user = request.user
        assert isinstance(user, User)

        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "Не передан id пользователя"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Users'])
    def get(self, request):
        """
        Получить всех пользователей
        """
        user = request.user
        assert isinstance(user, User)

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangeUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=['Users'],
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="id пользователя",
                required=True,
                type=int,
            ),
        ],
        request=UserCreateUpdateSerializer,
        responses=UserSerializer,
    )
    def patch(self, request):
        """
        Изменение пользователя \n
        Роли могут быть: `user` или `administrator` \n
        При тестировании через swagger необходимо убрать лишнее поля в примере `Schema`
        """
        user = request.user
        assert isinstance(user, User)
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response(
                {"error": "Нужно передать user_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Валидация user_id
        try:
            user_id = int(user_id)
        except ValueError:
            return Response(
                {"error": "user_id должен быть числом"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Поиск пользователя
        try:
            user_to_change = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Изменение параметров
        serializer = UserCreateUpdateSerializer(
            user_to_change,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            updated_user = serializer.save()

            password = request.data.get("password")
            if password:
                updated_user.set_password(password)
                updated_user.save()

            return Response(UserSerializer(updated_user).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Users'],
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="id пользователя",
                required=True,
                type=int,
            ),
        ],
    )
    def delete(self, request):
        """
        Удалить пользователя
        """
        user = request.user
        assert isinstance(user, User)
        user_id = request.query_params.get("user_id")

        # Валидация user_id
        try:
            user_id = int(user_id)
        except ValueError:
            return Response(
                {"error": "user_id должен быть числом"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка на 'себя'
        if user.id == user_id:
            return Response(
                {"error": "Нельзя удалить самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Взять и исключить администратора
        try:
            user_to_delete = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не существует"}, status=status.HTTP_404_NOT_FOUND)

        if user_to_delete.role == "administrator":
            return Response(
                {"error": "Нельзя удалить администратора"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Удаление
        user_to_delete.delete()
        return Response(
            {"message": f"Пользователь {user_id} успешно удален"},
            status=status.HTTP_200_OK
        )



