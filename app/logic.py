from django.utils.text import slugify
from enum import Enum
from typing import List, Tuple
import random
import secrets

from . import data, models


MINIMAL_INITIAL_SPAN_SIZE = len("<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>")
INITIAL_SPAN_STEP_FACTOR = 2.6180339887  # 1 + golden ratio, for no particular reason


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
    steps: List[int] = []
    current_stride = MINIMAL_INITIAL_SPAN_SIZE
    remaining = file_size
    while remaining >= current_stride * 2:
        steps.append(current_stride)
        remaining -= current_stride * 2
        current_stride = int(current_stride * INITIAL_SPAN_STEP_FACTOR + 0.5)
    pre_segments: List[Tuple[int, SpanInclusion]] = []
    for step in steps:
        pre_segments.append((step, SpanInclusion.Untested))
    middle: List[Tuple[int, SpanInclusion]] = []
    if remaining:
        middle.append((remaining, SpanInclusion.Untested))
    segments = pre_segments + middle + pre_segments[::-1]
    return segments


def create_new_version(version: models.ClipVersion, /, bug_present: bool) -> models.ClipVersion:
    raise NotImplementedError()
