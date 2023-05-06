from unittest import TestCase

import vapoursynth as vs

from vstools import (
    ColorRange,
    Matrix,
    Primaries,
    Transfer,
    UnsupportedMatrixError,
    UnsupportedPrimariesError,
    UnsupportedTransferError,
)


class TestMatrix(TestCase):
    def test_is_unknown(self) -> None:
        self.assertTrue(Matrix.is_unknown(Matrix.UNKNOWN))
        self.assertTrue(Matrix.is_unknown(2))
        self.assertFalse(Matrix.is_unknown(Matrix.RGB))
        self.assertFalse(Matrix.is_unknown(0))

    def test_from_res_rgb(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.RGB24)
        result = Matrix.from_res(clip)
        self.assertEqual(result, Matrix.RGB)

    def test_from_res_uhd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=3840, height=2160)
        result = Matrix.from_res(clip)
        self.assertEqual(result, Matrix.BT2020NC)

    def test_from_res_hd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        result = Matrix.from_res(clip)
        self.assertEqual(result, Matrix.BT709)

    def test_from_res_sd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=640, height=480)
        result = Matrix.from_res(clip)
        self.assertEqual(result, Matrix.SMPTE170M)

    def test_from_res_pal(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1024, height=576)
        result = Matrix.from_res(clip)
        self.assertEqual(result, Matrix.BT470BG)

    def test_from_video_rgb(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.RGB24)
        result = Matrix.from_video(clip)
        self.assertEqual(result, Matrix.RGB)

    def test_from_video_uhd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=3840, height=2160)
        result = Matrix.from_video(clip)
        self.assertEqual(result, Matrix.BT2020NC)

    def test_from_video_hd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        result = Matrix.from_video(clip)
        self.assertEqual(result, Matrix.BT709)

    def test_from_video_sd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=640, height=480)
        result = Matrix.from_video(clip)
        self.assertEqual(result, Matrix.SMPTE170M)

    def test_from_video_pal(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1024, height=576)
        result = Matrix.from_video(clip)
        self.assertEqual(result, Matrix.BT470BG)

    def test_from_transfer_unknown(self) -> None:
        result = Matrix.from_transfer(Transfer.BT709)
        self.assertEqual(result, Matrix.BT709)

    def test_from_transfer_unknown_strict(self) -> None:
        with self.assertRaises(UnsupportedTransferError):
            Matrix.from_transfer(Transfer.BT709, strict=True)

    def test_from_primaries_unknown(self) -> None:
        result = Matrix.from_primaries(Primaries.BT709)
        self.assertEqual(result, Matrix.BT709)

    def test_from_primaries_unknown_strict(self) -> None:
        with self.assertRaises(UnsupportedPrimariesError):
            Matrix.from_primaries(Primaries.BT709, strict=True)


class TestTransfer(TestCase):
    def test_is_unknown(self) -> None:
        self.assertTrue(Transfer.is_unknown(Transfer.UNKNOWN))
        self.assertTrue(Transfer.is_unknown(2))
        self.assertFalse(Transfer.is_unknown(Transfer.BT709))
        self.assertFalse(Transfer.is_unknown(1))

    def test_from_res_rgb(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.RGB24)
        result = Transfer.from_res(clip)
        self.assertEqual(result, Transfer.SRGB)

    def test_from_res_uhd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=3840, height=2160)
        result = Transfer.from_res(clip)
        self.assertEqual(result, Transfer.ST2084)

    def test_from_res_hd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        result = Transfer.from_res(clip)
        self.assertEqual(result, Transfer.BT709)

    def test_from_res_sd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=640, height=480)
        result = Transfer.from_res(clip)
        self.assertEqual(result, Transfer.BT601)

    def test_from_res_pal(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1024, height=576)
        result = Transfer.from_res(clip)
        self.assertEqual(result, Transfer.BT470BG)

    def test_from_video_rgb(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.RGB24)
        result = Transfer.from_video(clip)
        self.assertEqual(result, Transfer.SRGB)

    def test_from_video_uhd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=3840, height=2160)
        result = Transfer.from_video(clip)
        self.assertEqual(result, Transfer.ST2084)

    def test_from_video_hd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        result = Transfer.from_video(clip)
        self.assertEqual(result, Transfer.BT709)

    def test_from_video_sd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=640, height=480)
        result = Transfer.from_video(clip)
        self.assertEqual(result, Transfer.BT601)

    def test_from_video_pal(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1024, height=576)
        result = Transfer.from_video(clip)
        self.assertEqual(result, Transfer.BT470BG)

    def test_from_matrix(self) -> None:
        result = Transfer.from_matrix(Matrix.RGB)
        self.assertEqual(result, Transfer.SRGB)

        result = Transfer.from_matrix(Matrix.BT709)
        self.assertEqual(result, Transfer.BT709)

        result = Transfer.from_matrix(Matrix.BT470BG)
        self.assertEqual(result, Transfer.BT601)

        result = Transfer.from_matrix(Matrix.SMPTE170M)
        self.assertEqual(result, Transfer.BT601)

        result = Transfer.from_matrix(Matrix.SMPTE240M)
        self.assertEqual(result, Transfer.ST240M)

        result = Transfer.from_matrix(Matrix.CHROMA_DERIVED_C)
        self.assertEqual(result, Transfer.SRGB)

        result = Transfer.from_matrix(Matrix.ICTCP)
        self.assertEqual(result, Transfer.BT2020_10bits)

    def test_from_matrix_unknown(self) -> None:
        result = Transfer.from_matrix(Matrix.SMPTE2085)
        self.assertEqual(result, Transfer.XVYCC)

    def test_from_matrix_unknown_strict(self) -> None:
        with self.assertRaises(UnsupportedMatrixError):
            Transfer.from_matrix(Matrix.SMPTE2085, strict=True)

    def test_from_primaries_unknown(self) -> None:
        result = Transfer.from_primaries(Primaries.BT709)
        self.assertEqual(result, Transfer.BT709)

    def test_from_primaries_unknown_strict(self) -> None:
        with self.assertRaises(UnsupportedPrimariesError):
            Transfer.from_primaries(Primaries.BT709, strict=True)


class TestPrimaries(TestCase):
    def test_is_unknown(self) -> None:
        self.assertTrue(Primaries.is_unknown(Primaries.UNKNOWN))
        self.assertTrue(Primaries.is_unknown(2))
        self.assertFalse(Primaries.is_unknown(Primaries.BT709))
        self.assertFalse(Primaries.is_unknown(1))

    def test_from_res_rgb(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.RGB24)
        result = Primaries.from_res(clip)
        self.assertEqual(result, Primaries.BT709)

    def test_from_res_uhd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=3840, height=2160)
        result = Primaries.from_res(clip)
        self.assertEqual(result, Primaries.BT2020)

    def test_from_res_hd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        result = Primaries.from_res(clip)
        self.assertEqual(result, Primaries.BT709)

    def test_from_res_sd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=640, height=480)
        result = Primaries.from_res(clip)
        self.assertEqual(result, Primaries.ST170M)

    def test_from_res_pal(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1024, height=576)
        result = Primaries.from_res(clip)
        self.assertEqual(result, Primaries.BT470BG)

    def test_from_video_rgb(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.RGB24)
        result = Primaries.from_video(clip)
        self.assertEqual(result, Primaries.BT709)

    def test_from_video_uhd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=3840, height=2160)
        result = Primaries.from_video(clip)
        self.assertEqual(result, Primaries.BT2020)

    def test_from_video_hd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        result = Primaries.from_video(clip)
        self.assertEqual(result, Primaries.BT709)

    def test_from_video_sd(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=640, height=480)
        result = Primaries.from_video(clip)
        self.assertEqual(result, Primaries.ST170M)

    def test_from_video_pal(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1024, height=576)
        result = Primaries.from_video(clip)
        self.assertEqual(result, Primaries.BT470BG)

    def test_from_matrix_unknown(self) -> None:
        result = Primaries.from_matrix(Matrix.BT709)
        self.assertEqual(result, Primaries.BT709)

    def test_from_matrix_unknown_strict(self) -> None:
        with self.assertRaises(UnsupportedMatrixError):
            Primaries.from_matrix(Matrix.BT709, strict=True)

    def test_from_transfer_unknown(self) -> None:
        result = Primaries.from_transfer(Transfer.BT709)
        self.assertEqual(result, Primaries.BT709)

    def test_from_transfer_unknown_strict(self) -> None:
        with self.assertRaises(UnsupportedTransferError):
            Primaries.from_transfer(Transfer.BT709, strict=True)


class TestColorRange(TestCase):
    def test_from_res_rgb(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.RGB24)
        result = ColorRange.from_res(clip)
        self.assertEqual(result, ColorRange.FULL)

    def test_from_res_yuv(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8)
        result = ColorRange.from_res(clip)
        self.assertEqual(result, ColorRange.LIMITED)

    def test_from_video_rgb(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.RGB24)
        result = ColorRange.from_video(clip)
        self.assertEqual(result, ColorRange.FULL)

    def test_from_video_yuv(self) -> None:
        clip = vs.core.std.BlankClip(format=vs.YUV420P8)
        result = ColorRange.from_video(clip)
        self.assertEqual(result, ColorRange.LIMITED)

    def test_value_vs(self) -> None:
        self.assertEqual(ColorRange.LIMITED.value_vs, 1)
        self.assertEqual(ColorRange.FULL.value_vs, 0)

    def test_value_zimg(self) -> None:
        self.assertEqual(ColorRange.LIMITED.value_zimg, 0)
        self.assertEqual(ColorRange.FULL.value_zimg, 1)

    def test_value_is_limited(self) -> None:
        self.assertTrue(ColorRange.LIMITED.is_limited)
        self.assertFalse(ColorRange.FULL.is_limited)

    def test_value_is_full(self) -> None:
        self.assertFalse(ColorRange.LIMITED.is_full)
        self.assertTrue(ColorRange.FULL.is_full)
