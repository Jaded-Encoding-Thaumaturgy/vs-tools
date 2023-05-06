from unittest import TestCase

import vapoursynth as vs

from vstools import (
    Matrix,
    Primaries,
    Transfer,
    finalize_clip,
    get_prop,
    initialize_clip,
)


class TestClips(TestCase):
    def test_finalize_clip(self):
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        clip = finalize_clip(clip, clamp_tv_range=True)
        self.assertEqual(clip.format.bits_per_sample, 10)

        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        clip = finalize_clip(clip, clamp_tv_range=False)
        self.assertEqual(clip.format.bits_per_sample, 10)

        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        clip = finalize_clip(clip, bits=16)
        self.assertEqual(clip.format.bits_per_sample, 16)

        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        clip = finalize_clip(clip, bits=None)
        self.assertEqual(clip.format.bits_per_sample, 8)

    def test_initialize_clip(self):
        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        clip = initialize_clip(clip)
        self.assertEqual(clip.format.bits_per_sample, 16)
        self.assertEqual(get_prop(clip, "_Matrix", int), 1)
        self.assertEqual(get_prop(clip, "_Primaries", int), 1)
        self.assertEqual(get_prop(clip, "_Transfer", int), 1)

        clip = vs.core.std.BlankClip(format=vs.YUV420P8, width=1920, height=1080)
        clip = initialize_clip(
            clip,
            matrix=Matrix.SMPTE170M,
            transfer=Transfer.BT470BG,
            primaries=Primaries.BT470BG,
        )
        self.assertEqual(clip.format.bits_per_sample, 16)
        self.assertEqual(get_prop(clip, "_Matrix", int), 6)
        self.assertEqual(get_prop(clip, "_Primaries", int), 5)
        self.assertEqual(get_prop(clip, "_Transfer", int), 5)
