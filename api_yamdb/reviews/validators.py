from datetime import datetime as dt

from django.core.exceptions import ValidationError


def validate_year(value):
    year_today = dt.today().year
    if value > year_today:
        raise ValidationError(
            'Проверьте год выпуска!',
        )
    return value
