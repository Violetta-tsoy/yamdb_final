from csv import DictReader

from django.core.management import BaseCommand

from reviews.models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title,
    User,
)

ALREADY_LOADED_ERROR_MESSAGE = """
    If you need to reload the category, comments, genre,
    genre_title, review, titles, users data from the CSV file,
    first delete the db.sqlite3 file to destroy the database.
    Then, run `python manage.py migrate` for a new empty
    database with tables
"""

MODELS_FILES = [
    [
        Category,
        './static/data/category.csv',
    ],
    [
        Title,
        './static/data/titles.csv',
    ],
    [
        Genre,
        './static/data/genre.csv',
    ],
    [
        GenreTitle,
        './static/data/genre_title.csv',
    ],
    [
        Review,
        './static/data/review.csv',
    ],
    [
        Comment,
        './static/data/comments.csv',
    ],
    [
        User,
        './static/data/users.csv',
    ],
]


class Command(BaseCommand):
    help = "Loads data from csv"

    def handle(self, *args, **options):
        for model, file in MODELS_FILES:
            if model.objects.exists():
                print(f'data already loaded from {file} or already exists')
                print(ALREADY_LOADED_ERROR_MESSAGE)
                return

        print("Loading data")

        for row in DictReader(open('./static/data/category.csv')):
            Category(id=row['id'], name=row['name'], slug=row['slug']).save()

        for row in DictReader(open('./static/data/genre.csv')):
            Genre(id=row['id'], name=row['name'], slug=row['slug']).save()

        for row in DictReader(open('./static/data/titles.csv')):
            Title(
                id=row['id'],
                year=row['year'],
                name=row['name'],
                category_id=row['category'],
            ).save()

        for row in DictReader(open('./static/data/genre_title.csv')):
            GenreTitle(
                id=row['id'],
                title_id_id=row['title_id'],
                genre_id_id=row['genre_id'],
            ).save()

        for row in DictReader(open('./static/data/users.csv')):
            User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row['role'],
                bio=row['bio'],
            ).save()

        for row in DictReader(open('./static/data/review.csv')):
            Review(
                id=row['id'],
                title_id=row['title_id'],
                text=row['text'],
                author_id=row['author'],
                score=row['score'],
                pub_date=row['pub_date'],
            ).save()

        for row in DictReader(open('./static/data/comments.csv')):
            Comment(
                id=row['id'],
                review_id=row['review_id'],
                text=row['text'],
                author_id=row['author'],
                pub_date=row['pub_date'],
            ).save()

        return 'The data successfully loaded'
