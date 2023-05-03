from django.contrib import admin
from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('slug',)
    empty_value_display = ('-пусто-',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'year',
        'description',
    )


admin.site.register(Comment)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = (
        'username',
        'first_name',
        'last_name',
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title_id',
        'text',
        'author',
        'score',
        'pub_date',
    )
    search_fields = (
        'title_id',
        'text',
        'author',
        'score',
        'pub_date',
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = (
        'id',
        'name',
        'slug',
    )


admin.site.register(GenreTitle)
