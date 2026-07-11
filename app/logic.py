import random
import secrets
from django.utils.text import slugify

from . import data, models


def suggest_single_slug():
    words = random.choices(data.NICE_WORDS, k=2)
    number = random.randrange(1000, 10000)
    parts = []
    for w in words:
        parts.append(w.title())
    parts.append(str(number))
    return "".join(parts)


def suggest_slug():
    for _ in range(3):
        slug = suggest_single_slug()
        try:
            models.ClipProject.objects.get(slug=slug)
        except models.ClipProject.DoesNotExist:
            return slug
    return secrets.token_urlsafe()


def slugify_name(name):
    assert models.MAX_SLUG_LENGTH > 1 + 4
    base_slug = slugify(name)[:models.MAX_SLUG_LENGTH - 4]
    for _ in range(3):
        slug = base_slug + str(random.randrange(1000, 10000))
        try:
            models.ClipProject.objects.get(slug=slug)
        except models.ClipProject.DoesNotExist:
            return slug
    return secrets.token_urlsafe()
