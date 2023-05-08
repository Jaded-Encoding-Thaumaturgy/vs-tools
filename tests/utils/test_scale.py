from unittest import TestCase

from vstools import ColorRange, scale_8bit, scale_value, vs


class TestScale(TestCase):
    def test_scale_8bit_to_8bit(self) -> None:
        result = scale_8bit(vs.YUV420P8, 0)
        self.assertEqual(result, 0)

        result = scale_8bit(vs.YUV420P8, 24)
        self.assertEqual(result, 24)

        result = scale_8bit(vs.YUV420P8, 64)
        self.assertEqual(result, 64)

        result = scale_8bit(vs.YUV420P8, 255)
        self.assertEqual(result, 255)

    def test_scale_8bit_to_10bit(self) -> None:
        result = scale_8bit(vs.YUV420P10, 0)
        self.assertEqual(result, 0)

        result = scale_8bit(vs.YUV420P10, 24)
        self.assertEqual(result, 96)

        result = scale_8bit(vs.YUV420P10, 64)
        self.assertEqual(result, 256)

        result = scale_8bit(vs.YUV420P10, 255)
        self.assertEqual(result, 1020)

    def test_scale_8bit_to_float(self) -> None:
        result = scale_8bit(vs.YUV444PS, 0)
        self.assertEqual(result, 0)

        result = scale_8bit(vs.YUV444PS, 24)
        self.assertEqual(result, 0.09411764705882353)

        result = scale_8bit(vs.YUV444PS, 64)
        self.assertEqual(result, 0.25098039215686274)

        result = scale_8bit(vs.YUV444PS, 255)
        self.assertEqual(result, 1)

    def test_scale_value_no_change(self) -> None:
        result = scale_value(0, 8, 8)
        self.assertEqual(result, 0)

        result = scale_value(24, 8, 8)
        self.assertEqual(result, 24)

        result = scale_value(64, 8, 8)
        self.assertEqual(result, 64)

        result = scale_value(255, 8, 8)
        self.assertEqual(result, 255)

    def test_scale_value_to_10bit(self) -> None:
        result = scale_value(0, 8, 10)
        self.assertEqual(result, 0)

        result = scale_value(24, 8, 10)
        self.assertEqual(result, 96)

        result = scale_value(64, 8, 10)
        self.assertEqual(result, 256)

        result = scale_value(255, 8, 10)
        self.assertEqual(result, 1020)

    def test_scale_value_from_10bit(self) -> None:
        result = scale_value(0, 10, 8)
        self.assertEqual(result, 0)

        result = scale_value(96, 10, 8)
        self.assertEqual(result, 24)

        result = scale_value(256, 10, 8)
        self.assertEqual(result, 64)

        result = scale_value(1020, 10, 8)
        self.assertEqual(result, 255)

    def test_scale_value_to_float(self) -> None:
        result = scale_value(0, 8, vs.YUV444PS)
        self.assertEqual(result, 0)

        result = scale_value(24, 8, vs.YUV444PS)
        self.assertEqual(result, 0.09411764705882353)

        result = scale_value(64, 8, vs.YUV444PS)
        self.assertEqual(result, 0.25098039215686274)

        result = scale_value(255, 8, vs.YUV444PS)
        self.assertEqual(result, 1)

    def test_scale_value_from_float(self) -> None:
        result = scale_value(0, vs.YUV444PS, 8)
        self.assertEqual(result, 0)

        result = scale_value(0.1, vs.YUV444PS, 8)
        self.assertEqual(result, 25.5)

        result = scale_value(0.25, vs.YUV444PS, 8)
        self.assertEqual(result, 63.75)

        result = scale_value(1, vs.YUV444PS, 8)
        self.assertEqual(result, 255)

    def test_scale_value_to_limited(self) -> None:
        result = scale_value(
            0, 8, 8, range_in=ColorRange.FULL, range_out=ColorRange.LIMITED
        )
        self.assertEqual(result, 0)

        result = scale_value(
            24, 8, 8, range_in=ColorRange.FULL, range_out=ColorRange.LIMITED
        )
        self.assertEqual(result, 22.11764705882353)

        result = scale_value(
            64, 8, 8, range_in=ColorRange.FULL, range_out=ColorRange.LIMITED
        )
        self.assertEqual(result, 58.98039215686274)

        result = scale_value(
            255, 8, 8, range_in=ColorRange.FULL, range_out=ColorRange.LIMITED
        )
        self.assertEqual(result, 235)

    def test_scale_value_from_limited(self) -> None:
        result = scale_value(
            0, 8, 8, range_in=ColorRange.LIMITED, range_out=ColorRange.FULL
        )
        self.assertEqual(result, 0)

        result = scale_value(
            24, 8, 8, range_in=ColorRange.LIMITED, range_out=ColorRange.FULL
        )
        self.assertEqual(result, 26.04255319148936)

        result = scale_value(
            64, 8, 8, range_in=ColorRange.LIMITED, range_out=ColorRange.FULL
        )
        self.assertEqual(result, 69.44680851063829)

        result = scale_value(
            235, 8, 8, range_in=ColorRange.LIMITED, range_out=ColorRange.FULL
        )
        self.assertEqual(result, 254.99999999999997)
