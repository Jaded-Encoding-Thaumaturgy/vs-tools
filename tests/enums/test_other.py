from fractions import Fraction
from unittest import TestCase

from vstools import Dar, Direction, Region, Sar, get_prop, vs


class TestDirection(TestCase):
    def test_is_axis(self) -> None:
        self.assertTrue(Direction.HORIZONTAL.is_axis)
        self.assertTrue(Direction.VERTICAL.is_axis)
        self.assertFalse(Direction.LEFT.is_axis)
        self.assertFalse(Direction.RIGHT.is_axis)
        self.assertFalse(Direction.UP.is_axis)
        self.assertFalse(Direction.DOWN.is_axis)

    def test_is_way(self) -> None:
        self.assertFalse(Direction.HORIZONTAL.is_way)
        self.assertFalse(Direction.VERTICAL.is_way)
        self.assertTrue(Direction.LEFT.is_way)
        self.assertTrue(Direction.RIGHT.is_way)
        self.assertTrue(Direction.UP.is_way)
        self.assertTrue(Direction.DOWN.is_way)


class TestDar(TestCase):
    def test_from_size_width_height(self) -> None:
        result = Dar.from_size(1920, 1080)
        self.assertEqual(result, Dar(16, 9, 1080))

    def test_from_size_clip(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        result = Dar.from_size(clip)
        self.assertEqual(result, Dar(16, 9, 1080))

    def test_to_sar(self) -> None:
        self.assertEqual(Dar(16, 9, 1080).to_sar(1.0), Sar(1920, 1))


class TestSar(TestCase):
    def test_from_ar(self) -> None:
        self.assertEqual(Sar.from_ar(16, 9, 1080, 1.0), Sar(1920, 1))

    def test_from_dar(self) -> None:
        self.assertEqual(Sar.from_dar(Dar(16, 9, 1080), 1.0), Sar(1920, 1))

    def test_apply(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        clip = Sar(1920, 1).apply(clip)
        self.assertEqual(get_prop(clip, "_SARNum", int), 1920)
        self.assertEqual(get_prop(clip, "_SARDen", int), 1)


class TestRegion(TestCase):
    def test_framerate(self) -> None:
        self.assertEqual(Region.UNKNOWN.framerate, Fraction(0))
        self.assertEqual(Region.NTSC.framerate, Fraction(30000, 1001))
        self.assertEqual(Region.NTSCi.framerate, Fraction(60000, 1001))
        self.assertEqual(Region.PAL.framerate, Fraction(25, 1))
        self.assertEqual(Region.PALi.framerate, Fraction(50, 1))
        self.assertEqual(Region.FILM.framerate, Fraction(24, 1))
        self.assertEqual(Region.NTSC_FILM.framerate, Fraction(24000, 1001))

    def test_from_framerate(self) -> None:
        self.assertEqual(Region.from_framerate(Fraction(0)), Region.UNKNOWN)
        self.assertEqual(Region.from_framerate(Fraction(30000, 1001)), Region.NTSC)
        self.assertEqual(Region.from_framerate(Fraction(60000, 1001)), Region.NTSCi)
        self.assertEqual(Region.from_framerate(Fraction(25, 1)), Region.PAL)
        self.assertEqual(Region.from_framerate(Fraction(50, 1)), Region.PALi)
        self.assertEqual(Region.from_framerate(Fraction(24, 1)), Region.FILM)
        self.assertEqual(Region.from_framerate(Fraction(24000, 1001)), Region.NTSC_FILM)
