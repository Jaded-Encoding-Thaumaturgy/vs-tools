from unittest import TestCase

from vstools import ChromaLocation, FieldBased, Resolution, UnsupportedFieldBasedError, vs


class TestChromaLocation(TestCase):
    def test_from_res_uhd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=3840, height=2160)
        result = ChromaLocation.from_res(clip)
        self.assertEqual(result, ChromaLocation.LEFT)

    def test_from_res_hd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        result = ChromaLocation.from_res(clip)
        self.assertEqual(result, ChromaLocation.LEFT)

    def test_from_res_sd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=640, height=480)
        result = ChromaLocation.from_res(clip)
        self.assertEqual(result, ChromaLocation.LEFT)

    def test_from_video_uhd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=3840, height=2160)
        result = ChromaLocation.from_video(clip)
        self.assertEqual(result, ChromaLocation.LEFT)

    def test_from_video_hd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        result = ChromaLocation.from_video(clip)
        self.assertEqual(result, ChromaLocation.LEFT)

    def test_from_video_sd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=640, height=480)
        result = ChromaLocation.from_video(clip)
        self.assertEqual(result, ChromaLocation.LEFT)

    def test_get_offsets_from_chroma_location(self) -> None:
        off_left, off_top = ChromaLocation.get_offsets(ChromaLocation.LEFT)
        self.assertEqual(off_left, -0.5)
        self.assertEqual(off_top, 0.0)

        off_left, off_top = ChromaLocation.get_offsets(ChromaLocation.CENTER)
        self.assertEqual(off_left, 0.0)
        self.assertEqual(off_top, 0.0)

        off_left, off_top = ChromaLocation.get_offsets(ChromaLocation.TOP_LEFT)
        self.assertEqual(off_left, -0.5)
        self.assertEqual(off_top, -0.5)

        off_left, off_top = ChromaLocation.get_offsets(ChromaLocation.TOP)
        self.assertEqual(off_left, 0.0)
        self.assertEqual(off_top, -0.5)

        off_left, off_top = ChromaLocation.get_offsets(ChromaLocation.BOTTOM_LEFT)
        self.assertEqual(off_left, -0.5)
        self.assertEqual(off_top, 0.5)

        off_left, off_top = ChromaLocation.get_offsets(ChromaLocation.BOTTOM)
        self.assertEqual(off_left, 0.0)
        self.assertEqual(off_top, 0.5)

    def test_get_offsets_from_video(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8)
        off_left, off_top = ChromaLocation.get_offsets(clip)
        self.assertEqual(off_left, 0.5)
        self.assertEqual(off_top, 0.0)

        clip = vs.core.std.BlankClip(format=vs.YUV422P8)
        off_left, off_top = ChromaLocation.get_offsets(clip)
        self.assertEqual(off_left, 0.5)
        self.assertEqual(off_top, 0.0)

        clip = vs.core.std.BlankClip(format=vs.YUV444P8)
        off_left, off_top = ChromaLocation.get_offsets(clip)
        self.assertEqual(off_left, 0.0)
        self.assertEqual(off_top, 0.0)

        clip = vs.core.std.BlankClip(format=vs.YUV411P8)
        off_left, off_top = ChromaLocation.get_offsets(clip)
        self.assertEqual(off_left, 2.5)
        self.assertEqual(off_top, 0.0)

        clip = vs.core.std.BlankClip(format=vs.YUV410P8)
        off_left, off_top = ChromaLocation.get_offsets(clip)
        self.assertEqual(off_left, 2.5)
        self.assertEqual(off_top, 1.0)


class TestFieldBased(TestCase):
    def test_from_res(self) -> None:
        clip = vs.core.std.BlankClip()
        result = FieldBased.from_res(clip)
        self.assertEqual(result, FieldBased.PROGRESSIVE)

        clip = vs.core.std.BlankClip(format=vs.YUV420P8)
        result = FieldBased.from_res(clip)
        self.assertEqual(result, FieldBased.PROGRESSIVE)

    def test_from_video(self) -> None:
        clip = vs.core.std.BlankClip()
        result = FieldBased.from_video(clip)
        self.assertEqual(result, FieldBased.PROGRESSIVE)

        clip = vs.core.std.BlankClip(format=vs.YUV420P8)
        result = FieldBased.from_video(clip)
        self.assertEqual(result, FieldBased.PROGRESSIVE)

    def test_is_inter(self) -> None:
        self.assertTrue(FieldBased.TFF.is_inter)
        self.assertTrue(FieldBased.BFF.is_inter)
        self.assertFalse(FieldBased.PROGRESSIVE.is_inter)

    def test_field(self) -> None:
        self.assertEqual(FieldBased.TFF.field, 1)
        self.assertEqual(FieldBased.BFF.field, 0)
        with self.assertRaises(UnsupportedFieldBasedError):
            FieldBased.PROGRESSIVE.field

    def test_is_tff(self) -> None:
        self.assertTrue(FieldBased.TFF.is_tff)
        self.assertFalse(FieldBased.BFF.is_tff)
        self.assertFalse(FieldBased.PROGRESSIVE.is_tff)


class TestResolution(TestCase):
    def test_from_video(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=640, height=480)
        self.assertEqual(Resolution.from_video(clip), (640, 480))

        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        self.assertEqual(Resolution.from_video(clip), (1920, 1080))
