from django.db.models import Q
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
        )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            'name',
            'slug',
        )

    def validate_slug(self, value):
        if Genre.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                'В POST-запросе администратора'
                'передан уже существующий `slug` '
            )
        return value


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(
        many=True,
    )
    category = CategorySerializer()
    rating = serializers.IntegerField(
        default=None,
        read_only=True,
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'genre',
            'category',
            'description',
            'rating',
        )


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'genre',
            'category',
            'description',
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id',
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'author',
            'text',
            'score',
            'title',
            'pub_date',
        )

    def validate(self, data):
        if self.context.get('request').method == 'POST':
            title_id = self.context.get('view').kwargs.get(
                'title_id',
            )
            author = self.context.get('request').user
            title = get_object_or_404(
                Title,
                id=title_id,
            )
            if title.reviews.filter(author=author).exists():
                raise serializers.ValidationError(
                    'Можно оставлять только один отзыв',
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=254,
        allow_blank=False,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ],
    )
    username = serializers.SlugField(
        max_length=150,
        allow_blank=False,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ],
    )
    first_name = serializers.CharField(
        max_length=150,
        required=False,
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
    )
    bio = serializers.CharField(
        max_length=255,
        required=False,
    )

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = User

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Username "me" is not valid',
            )
        return value


class SignUpSerializer(serializers.Serializer):
    username = serializers.SlugField(
        max_length=150,
        allow_blank=False,
    )
    email = serializers.EmailField(
        max_length=254,
        allow_blank=False,
    )

    def create(self, validated_data):
        user = User.objects.filter(
            Q(email=validated_data['email'])
            | Q(username=validated_data['username'])
        )
        if user:
            raise serializers.ValidationError(
                'username or email is already registered'
            )
        return User.objects.create(**validated_data)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Username "me" is not valid',
            )
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    confirmation_code = serializers.CharField(max_length=36)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Username "me" is not valid',
            )
        return value
