from collections import Counter
from django.test import TestCase

from . import logic


class LogicTests(TestCase):
    def testSingleSlugsDontEasilyRepeat(self) -> None:
        counts = Counter(logic.suggest_single_slug() for _ in range(30))
        problem_names = {k for k, v in counts.items() if v > 1}
        self.assertFalse(problem_names)

    def testSlugsDontEasilyRepeat(self) -> None:
        counts = Counter(logic.suggest_slug() for _ in range(30))
        problem_names = {k for k, v in counts.items() if v > 1}
        self.assertFalse(problem_names)

    def testNameSlugsDontEasilyRepeat(self) -> None:
        # Only have 9000 possible names for a given name.
        # Choosing 1000 independent names (that don't occur yet in the DB, but also never get added to it)
        # means there's only a probability of 7e-13 that we see any element more than 10 times.
        # (Hint: Assume the distribution is Poisson(1/9) and observe that P(k=10)=7e-17, P(k=11)=7e-19.)
        # This means that the following test has a false-positive rate of 7e-13, i.e. "never".
        # So if you see this fail, something is very probably broken.
        # If you see this fail twice, something is *definitely* broken.
        some_name = "Hello!"
        counts = Counter(logic.slugify_name(some_name) for _ in range(1000))
        problem_names = {k: v for k, v in counts.items() if v >= 10}
        self.assertFalse(problem_names)

    def testNameSlugsHaveNicePrefixes(self) -> None:
        data = [
            ("Hello", "hello"),
            ("¿Holá?", "hola"),
            ("äöüß", "aou"),
            ("Friede, Freude und Eierkuchen.html", "friede-freude-und-eierkuchenhtml"),
            (
                "This is ridiculous. You can't just put an entire sentence, or, in fact, two, into a filename, and expect nothing to be cut off!.svg.com.html",
                "this-is-ridiculous-you-cant-just-put-an-entire",
            ),
        ]
        for entry in data:
            with self.subTest(entry=entry):
                file_name, expected_prefix = entry
                slug = logic.slugify_name(file_name)
                self.assertEqual(slug[:-4], expected_prefix, slug)

    def testSpansCover(self) -> None:
        for length in range(1000):
            with self.subTest(length=length):
                spans: logic.Spans = logic.make_span_list(length)
                total_length = 0
                for i, span in enumerate(spans):
                    total_length += span[0]
                    self.assertEqual(span[1], logic.SpanInclusion.Untested, i)
                self.assertEqual(total_length, length)

    def testSpansMeaningfulLarge(self) -> None:
        spans_raw = logic.make_span_list(123456)
        self.assertTrue(all(span[1] == logic.SpanInclusion.Untested for span in spans_raw))
        lengths_actual = [s[0] for s in spans_raw]
        # Hardcoded values, taken trom the actual output and sanity-checked by applying my eyeballs.
        lengths_expected = [
            59,
            154,
            403,
            1055,
            2762,
            7231,
            18931,
            62266,
            18931,
            7231,
            2762,
            1055,
            403,
            154,
            59,
        ]
        self.assertEqual(lengths_expected, lengths_actual)
