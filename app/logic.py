from django.utils.text import slugify
from enum import Enum
from typing import List, Tuple
import random
import secrets

from . import data, models


class SpanInclusion(Enum):
    Untested = 1
    CannotBeCompletelyRemoved = 2
    Skip = 3
    CurrentTest = 4


def suggest_single_slug() -> str:
    words = random.choices(data.NICE_WORDS, k=2)
    number = random.randrange(1000, 10000)
    parts = []
    for w in words:
        parts.append(w.title())
    parts.append(str(number))
    return "".join(parts)


def suggest_slug() -> str:
    for _ in range(3):
        slug = suggest_single_slug()
        try:
            models.ClipProject.objects.get(slug=slug)
        except models.ClipProject.DoesNotExist:
            return slug
    return secrets.token_urlsafe()


def slugify_name(name: str) -> str:
    assert models.MAX_SLUG_LENGTH > 1 + 4
    base_slug = slugify(name)[:models.MAX_SLUG_LENGTH - 4]
    for _ in range(3):
        slug = base_slug + str(random.randrange(1000, 10000))
        try:
            models.ClipProject.objects.get(slug=slug)
        except models.ClipProject.DoesNotExist:
            return slug
    return secrets.token_urlsafe()


def make_segment_list(file_size: int) -> List[Tuple[int, SpanInclusion]]:
    raise NotImplementedError()


def create_new_version(version: models.ClipVersion, /, bug_present: bool) -> models.ClipVersion:
    raise NotImplementedError()
