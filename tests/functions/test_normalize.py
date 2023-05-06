from unittest import TestCase

import vapoursynth as vs

from vstools import flatten, normalize_ranges


class TestNormalize(TestCase):
    def test_flatten(self) -> None:
        result = flatten(["a", "b", ["c", "d", ["e"]]])
        self.assertEqual(list(result), ["a", "b", "c", "d", "e"])

    def test_normalize_ranges(self) -> None:
        clip = vs.core.std.BlankClip(length=1000)

        self.assertEqual(normalize_ranges(clip, (None, None)), [(0, 1000)])
        self.assertEqual(normalize_ranges(clip, (24, -24)), [(24, 976)])
        self.assertEqual(normalize_ranges(clip, [(24, 100), (80, 150)]), [(24, 150)])
