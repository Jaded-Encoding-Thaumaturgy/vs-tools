from unittest import TestCase

import vapoursynth as vs

from vstools import fallback, iterate, kwargs_fallback


class TestFuncs(TestCase):
    def test_iterate(self) -> None:
        result = iterate(5, lambda x: x * 2, 2)
        self.assertEqual(result, 20)

    def test_iterate_clip(self) -> None:
        clip = vs.core.std.BlankClip()
        result = iterate(clip, vs.core.std.Maximum, 3, threshold=0.5)
        self.assertEqual(type(result), vs.VideoNode)

    def test_fallback(self) -> None:
        self.assertEqual(fallback(5, 6), 5)
        self.assertEqual(fallback(None, 6), 6)

    def test_kwargs_fallback(self) -> None:
        kwargs = dict(
            overlap=1, search=2, block_size=4, sad_mode=8, motion=12, thSAD=16
        )
        self.assertEqual(kwargs_fallback(5, (kwargs, "block_size"), 8), 5)
        self.assertEqual(kwargs_fallback(None, (kwargs, "block_size"), 8), 4)
        self.assertEqual(kwargs_fallback(None, (dict(), "block_size"), 8), 8)
