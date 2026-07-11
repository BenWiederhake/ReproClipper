from django.utils.text import slugify
from enum import Enum
from typing import List, Optional, Tuple
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
    spans: Spans = []
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


def resolve_span_test(spans: Spans, bug_present: bool) -> Spans:
    new_spans: Spans = []
    for span in spans:
        if span[1] == SpanInclusion.CurrentTest:
            if not bug_present:
                # Something in this span was important for reproducing the bug, so leave it in for now.
                if span[0] > 1:
                    first_half = span[0] // 2
                    second_half = span[0] - first_half
                    new_spans.append((first_half, SpanInclusion.Untested))
                    new_spans.append((second_half, SpanInclusion.Untested))
                else:
                    new_spans.append((span[0], SpanInclusion.CannotBeCompletelyRemoved))
                continue  # Current span handled
            # Leaving the span out means the bug is still present, so we can leave it out to minimize the reproducer:
            span = (span[0], SpanInclusion.Skip)
            # However, we can't add it to new_spans yet, as it might collapse with surrounding spans.
        if span[1] == SpanInclusion.Skip and new_spans and new_spans[-1][1] == SpanInclusion.Skip:
            # Extend the old span:
            old_length: int = new_spans[-1][0]
            new_spans[-1] = (old_length + span[0], SpanInclusion.Skip)
            continue
        new_spans.append(span)
    if new_spans and new_spans[-1][1] == SpanInclusion.Skip:
        new_spans.pop()
        assert not (new_spans and new_spans[-1][1] == SpanInclusion.Skip)
    return new_spans


def find_biggest_untested_span(spans: Spans) -> Optional[int]:
    index_of_biggest: Optional[int] = None
    size_of_biggest: Optional[int] = None
    for i, span in enumerate(spans):
        if span[1] == SpanInclusion.CannotBeCompletelyRemoved:
            assert span[0] == 1
            continue
        elif span[1] == SpanInclusion.CurrentTest:
            raise AssertionError()
        elif span[1] == SpanInclusion.Skip:
            continue
        # else: pass
        assert span[1] == SpanInclusion.Untested
        if size_of_biggest is None or size_of_biggest < span[0]:
            size_of_biggest = span[0]
            index_of_biggest = i
    return index_of_biggest


def create_new_unsaved_version(parent_version: models.ClipVersion) -> models.ClipVersion:
    parent_spans = spans_decode(parent_version.span_list_converted_to_str)
    resolved_spans = resolve_span_test(parent_spans, parent_version.bug_present)
    index_of_biggest = find_biggest_untested_span(resolved_spans)
    assert index_of_biggest is not None  # TODO: "Congratulations, you're using the tool wrong"-view
    test_span = resolved_spans[index_of_biggest]
    resolved_spans[index_of_biggest] = (test_span[0], SpanInclusion.CurrentTest)
    version = models.ClipVersion(
        parent_project=parent_version.parent_project,
        parent_version=parent_version,
        bug_present=None,  # Wasn't tested by the user yet
        amount_of_times_loaded=0,
        span_list_converted_to_str=spans_encode(resolved_spans),
        last_datetime_loaded=None,
        # created_datetime is automatic
        decided_datetime=None,
    )
    return version


def reconstruct_content(version: models.ClipVersion) -> bytes:
    base_content: bytes = version.parent_project.base_file.read()
    spans: Spans = spans_decode(version.span_list_converted_to_str)
    parts: List[bytes] = []
    offset = 0
    for span in spans:
        start = offset
        offset += span[0]
        end = offset
        if span[1] == SpanInclusion.CannotBeCompletelyRemoved:
            pass  # Included
        elif span[1] == SpanInclusion.CurrentTest:
            continue  # Skipped, for now
        elif span[1] == SpanInclusion.Skip:
            continue  # Skipped
        elif span[1] == SpanInclusion.Untested:
            pass  # Included
        else:
            raise AssertionError(span)
        parts.append(base_content[start:end])
    return b"".join(parts)


SKIPPED_SPANS: List[SpanInclusion] = [SpanInclusion.Untested, SpanInclusion.CannotBeCompletelyRemoved]


def compute_size_linear(version: models.ClipVersion) -> int:
    spans = spans_decode(version.span_list_converted_to_str)
    return sum(s[0] for s in spans if s[1] in SKIPPED_SPANS)


# Finally, overwrite the function in module "models":
models.lazy_init_fn__compute_size_linear = compute_size_linear
