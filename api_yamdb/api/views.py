import uuid

from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import decorators, filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api import permissions, serializers
from api.filters import TitleFilter
from reviews import models


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAdmin,
    ]
    queryset = models.Title.objects.annotate(
        rating=Avg('reviews__score'),
    )
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    ordering = ('-rating',)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.TitleReadSerializer
        return serializers.TitleCreateSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return [
                permissions.IsAdminOrReadOnly(),
            ]
        return super().get_permissions()


class CategoryGenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [
        permissions.IsAdmin,
    ]
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'list':
            return [
                permissions.IsAdminOrReadOnly(),
            ]
        return super().get_permissions()


class CategoryViewSet(CategoryGenreViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    queryset = models.Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    permission_classes = [
        permissions.ForReview,
    ]

    def get_queryset(self):
        review_id = get_object_or_404(
            models.Review,
            pk=self.kwargs.get('review_id'),
        )
        return models.Comment.objects.filter(
            review=review_id,
        )

    def perform_create(self, serializer):
        review = get_object_or_404(
            models.Review,
            pk=self.kwargs.get('review_id'),
        )
        serializer.save(
            author=self.request.user,
            review=review,
        )


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.ForReview,
    ]
    serializer_class = serializers.ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(
            models.Title,
            pk=self.kwargs.get('title_id'),
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            models.Title,
            pk=self.kwargs.get('title_id'),
        )
        serializer.save(
            author=self.request.user,
            title=title,
        )


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAdmin,
    ]
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
    ]
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = ('username',)
    lookup_field = 'username'

    @decorators.action(
        methods=[
            'GET',
            'PATCH',
        ],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def me(self, request, *args, **kwargs):
        serializer = serializers.UserSerializer(
            request.user,
        )
        if request.method == 'PATCH':
            serializer = serializers.UserSerializer(
                request.user,
                data=request.data,
                partial=True,
            )
            if serializer.is_valid(raise_exception=True):
                serializer.validated_data['role'] = request.user.role
                serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class AuthViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()

    def get_serializer_class(self):
        if self.action == 'signup':
            return serializers.SignUpSerializer
        return serializers.TokenSerializer

    @action(detail=False, methods=['POST'])
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = self.queryset.filter(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
            )
            if user.exists():
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK,
                )
            serializer.save()
            user = user.first()
            user.confirmation_code = str(uuid.uuid4())
            user.save()
            send_mail(
                message=f'confirmation code: {user.confirmation_code}',
                recipient_list=[user.email],
                subject='confirmation code',
                from_email='kob87@list.ru',
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def token(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = get_object_or_404(
                self.queryset,
                username=serializer.data['username'],
            )
            if serializer.data['confirmation_code'] != user.confirmation_code:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken.for_user(user)
            return Response(
                {'token': str(token.access_token)},
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
