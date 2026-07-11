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


# Number of bytes, and what to do with these bytes.
SingleSpan = Tuple[int, SpanInclusion]
Spans = List[SingleSpan]


def spans_encode(spans: Spans) -> str:
    parts: List[str] = []
    for span in spans:
        parts.append(str(span[0]))
        parts.append(str(span[1].value))
    return ",".join(parts)


def spans_decode(serialized: str) -> Spans:
    parts_int = [int(p) for p in serialized.split(",")]
    spans = Spans()
    assert len(parts_int) % 2 == 0
    for i in range(len(parts_int) // 2):
        seg = (parts_int[i * 2], SpanInclusion(parts_int[i * 2 + 1]))
        spans.append(seg)
    return spans


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


def make_span_list(file_size: int) -> Spans:
    steps: List[int] = []
    current_stride = MINIMAL_INITIAL_SPAN_SIZE
    remaining = file_size
    while remaining >= current_stride * 2:
        steps.append(current_stride)
        remaining -= current_stride * 2
        current_stride = int(current_stride * INITIAL_SPAN_STEP_FACTOR + 0.5)
    pre_segments: Spans = []
    for step in steps:
        pre_segments.append((step, SpanInclusion.Untested))
    middle: Spans = []
    if remaining:
        middle.append((remaining, SpanInclusion.Untested))
    segments = pre_segments + middle + pre_segments[::-1]
    return segments


def create_new_version(parent_version: models.ClipVersion, /, bug_present: bool) -> models.ClipVersion:
    raise NotImplementedError()
