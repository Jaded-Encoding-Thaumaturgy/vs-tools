from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, ClassVar, Iterable, NamedTuple, TypeVar, overload

import vapoursynth as vs

from ..enums import SceneChangeMode, Matrix
from ..exceptions import CustomValueError, FramesLengthError
from ..types import FilePathType, FuncExceptT, Sentinel
from .render import clip_async_render

__all__ = [
    'Timecodes',
    'Keyframes',
    'LWIndex'
]


@dataclass
class Timecode:
    frame: int
    numerator: int
    denominator: int

    def to_fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Timecode):
            return False

        return (self.numerator, self.denominator) == (other.numerator, other.denominator)

    def __int__(self) -> float:
        return self.frame

    def __float__(self) -> float:
        return float(self.to_fraction())


TimecodeBoundT = TypeVar('TimecodeBoundT', bound=Timecode)


class Timecodes(list[Timecode]):
    V1 = 1
    V2 = 2

    def to_fractions(self) -> list[Fraction]:
        return list(
            Fraction(x.numerator, x.denominator)
            for x in self
        )

    def to_normalized_ranges(self) -> dict[tuple[int, int], Fraction]:
        timecodes_ranges = dict[tuple[int, int], Fraction]()

        last_i = len(self) - 1
        last_tcode: tuple[int, Timecode] = (0, self[0])

        for tcode in self[1:]:
            start, ltcode = last_tcode

            if tcode != ltcode:
                timecodes_ranges[start, tcode.frame - 1] = ltcode.to_fraction()
                last_tcode = (tcode.frame, tcode)
            elif tcode.frame == last_i:
                timecodes_ranges[start, tcode.frame + 1] = tcode.to_fraction()

        return timecodes_ranges

    @classmethod
    def normalize_range_timecodes(
        cls, timecodes: dict[tuple[int | None, int | None], Fraction], end: int, assume: Fraction | None = None
    ) -> list[Fraction]:
        from .funcs import fallback

        norm_timecodes = [assume] * end if assume else list[Fraction]()

        for (startn, endn), fps in timecodes.items():
            start = max(fallback(startn, 0), 0)
            end = fallback(endn, end)

            if end > len(norm_timecodes):
                norm_timecodes += [fps] * (end - len(norm_timecodes))

            norm_timecodes[start:end + 1] = [fps] * (end - start)

        return norm_timecodes

    @classmethod
    def separate_norm_timecodes(cls, timecodes: Timecodes | dict[tuple[int, int], Fraction]) -> tuple[
        Fraction, dict[tuple[int, int], Fraction]
    ]:
        if isinstance(timecodes, Timecodes):
            timecodes = timecodes.to_normalized_ranges()

        times_count = {k: 0 for k in timecodes.values()}

        for v in timecodes.values():
            times_count[v] += 1

        major_count = max(times_count.values())
        major_time = next(t for t, c in times_count.items() if c == major_count)
        minor_fps = {r: v for r, v in timecodes.items() if v != major_time}

        return major_time, minor_fps

    @classmethod
    def accumulate_norm_timecodes(cls, timecodes: Timecodes | dict[tuple[int, int], Fraction]) -> tuple[
        Fraction, dict[Fraction, list[tuple[int, int]]]
    ]:
        if isinstance(timecodes, Timecodes):
            timecodes = timecodes.to_normalized_ranges()

        major_time, minor_fps = cls.separate_norm_timecodes(timecodes)

        acc_ranges = dict[Fraction, list[tuple[int, int]]]()

        for k, v in minor_fps.items():
            if v not in acc_ranges:
                acc_ranges[v] = []

            acc_ranges[v].append(k)

        return major_time, acc_ranges

    @classmethod
    def from_clip(cls: type[TimecodesBoundT], clip: vs.VideoNode, **kwargs: Any) -> TimecodesBoundT:
        if hasattr(vs.core, 'akarin'):
            prop_clip = clip.std.BlankClip(2, 1, vs.GRAY16, keep=True).std.CopyFrameProps(clip)
            prop_clip = prop_clip.akarin.Expr('X 1 = x._DurationNum x._DurationDen ?')

            def _get_timecode(n: int, f: vs.VideoFrame) -> Timecode:
                return Timecode(n, (m := f[0])[0, 0], m[0, 1])  # type: ignore
        else:
            prop_clip = clip

            def _get_timecode(n: int, f: vs.VideoFrame) -> Timecode:
                return Timecode(n, f.props._DurationNum, f.props._DurationDen)  # type: ignore

        return cls(clip_async_render(prop_clip, None, '', _get_timecode, **kwargs))

    @overload
    @classmethod
    def from_file(
        cls: type[TimecodesBoundT], file: FilePathType, ref: vs.VideoNode, *, func: FuncExceptT | None = None
    ) -> TimecodesBoundT:
        ...

    @overload
    @classmethod
    def from_file(
        cls: type[TimecodesBoundT],
        file: FilePathType, length: int, den: int | None = None, *, func: FuncExceptT | None = None
    ) -> TimecodesBoundT:
        ...

    @classmethod  # type: ignore
    def from_file(
        cls: type[TimecodesBoundT], file: FilePathType, ref_or_length: int | vs.VideoNode, den: int | None = None,
        *, func: FuncExceptT | None = None
    ) -> TimecodesBoundT:
        func = func or cls.from_file

        file = Path(str(file)).resolve()

        length = ref_or_length if isinstance(ref_or_length, int) else ref_or_length.num_frames

        fb_den = (
            None if ref_or_length.fps_den in {0, 1} else ref_or_length.fps_den  # type: ignore
        ) if isinstance(ref_or_length, vs.VideoNode) else None

        denominator = den or fb_den or 1001

        version, *_timecodes = file.read_text().splitlines()

        if 'v1' in version:
            def _norm(xd: str) -> Fraction:
                return Fraction(int(denominator * float(xd)), denominator)

            assume = None

            timecodes_d = dict[tuple[int | None, int | None], Fraction]()

            for line in _timecodes:
                if line.startswith('#'):
                    continue

                if line.startswith('Assume'):
                    assume = _norm(_timecodes[0][7:])
                    continue

                starts, ends, _fps = line.split(',')
                timecodes_d[(int(starts), int(ends) + 1)] = _norm(_fps)

            norm_timecodes = cls.normalize_range_timecodes(timecodes_d, length, assume)
        elif 'v2' in version:
            timecodes_l = [float(t) for t in _timecodes if not t.startswith('#')]
            norm_timecodes = [
                Fraction(int(denominator / float(f'{round((x - y) * 100, 4) / 100000:.08f}'[:-1])), denominator)
                for x, y in zip(timecodes_l[1:], timecodes_l[:-1])
            ]
        else:
            raise CustomValueError('timecodes file not supported!', func, file)

        if len(norm_timecodes) != length:
            raise FramesLengthError(
                func, '', 'timecodes file length mismatch with specified length!',
                reason=dict(timecodes=len(norm_timecodes), clip=length)
            )

        return cls(
            Timecode(i, f.numerator, f.denominator) for i, f in enumerate(norm_timecodes)
        )

    def assume_vfr(self, clip: vs.VideoNode, func: FuncExceptT | None = None) -> vs.VideoNode:
        from ..utils import replace_ranges

        func = func or self.assume_vfr

        major_time, minor_fps = self.accumulate_norm_timecodes(self)

        assumed_clip = clip.std.AssumeFPS(None, major_time.numerator, major_time.denominator)

        for other_fps, fps_ranges in minor_fps.items():
            assumed_clip = replace_ranges(
                assumed_clip, clip.std.AssumeFPS(None, other_fps.numerator, other_fps.denominator),
                fps_ranges, False, False, False
            )

        return assumed_clip

    def to_file(self, out: FilePathType, format: int = V2, func: FuncExceptT | None = None) -> None:
        from ..utils import check_perms

        func = func or self.to_file

        out_path = Path(str(out)).resolve()

        check_perms(out_path, 'w+', func=func)

        out_text = [
            f'# timecode format v{format}'
        ]

        if format == Timecodes.V1:
            major_time, minor_fps = self.separate_norm_timecodes(self)

            out_text.append(f'Assume {round(float(major_time), 12)}')

            out_text.extend([
                ','.join(map(str, [*frange, round(float(fps), 12)]))
                for frange, fps in minor_fps.items()
            ])
        elif format == Timecodes.V2:
            acc = 0.0
            for time in self:
                s_acc = str(round(acc / 100, 12) * 100)
                l, i = len(s_acc), s_acc.index('.')
                d = l - i - 1
                if d < 6:
                    s_acc += '0' * (6 - d)
                else:
                    s_acc = s_acc[:i + 7]

                out_text.append(s_acc)
                acc += (time.denominator * 100) / (time.numerator * 100) * 1000
            out_text.append(str(acc))
        else:
            raise CustomValueError('timecodes format not supported!', func, format)

        out_path.unlink(True)
        out_path.touch()
        out_path.write_text('\n'.join(out_text + ['']))


TimecodesBoundT = TypeVar('TimecodesBoundT', bound=Timecodes)


class Keyframes(list[int]):
    V1 = 1
    XVID = -1

    WWXD: ClassVar = SceneChangeMode.WWXD
    SCXVID: ClassVar = SceneChangeMode.SCXVID

    def __init__(self, iterable: Iterable[int], end_frame: int) -> None:
        super().__init__(iterable)

        self.end_frame = end_frame

    @classmethod
    def from_clip(cls: type[KeyframesBoundT], clip: vs.VideoNode, mode: SceneChangeMode = WWXD) -> KeyframesBoundT:
        from ..utils import get_prop, get_w

        clip = clip.resize.Bilinear(get_w(360, clip), 360, format=vs.YUV420P8)
        clip = mode.ensure_presence(clip)

        frames = clip_async_render(
            clip, None, 'Detecting scene changes...', lambda n, f: Sentinel.check(
                n, all(get_prop(f, key, int) == 1 for key in mode.prop_keys)
            )
        )

        return cls(sorted(list(Sentinel.filter(frames))), clip.num_frames)

    def to_file(self, out: FilePathType, format: int = V1, func: FuncExceptT | None = None) -> None:
        from ..utils import check_perms

        func = func or self.to_file

        out_path = Path(str(out)).resolve()

        check_perms(out_path, 'w+', func=func)

        if format == Keyframes.V1:
            out_text = [
                '# keyframe format v1', 'fps 0', '', *map(str, self), ''
            ]
        elif format == Keyframes.XVID:
            lut_self = set(self)
            out_text = [
                '# XviD 2pass stat file', '',
                *(
                    (lut_self.remove(i) or 'i') if i in lut_self else 'b'  # type: ignore
                    for i in range(self.end_frame)
                )
            ]

        out_path.unlink(True)
        out_path.touch()
        out_path.write_text('\n'.join(out_text))


KeyframesBoundT = TypeVar('KeyframesBoundT', bound=Keyframes)


@dataclass
class LWIndex:
    stream_info: StreamInfo
    frame_data: list[Frame]
    keyframes: Keyframes

    class Regex:
        frame_first = re.compile(
            r"Index=(?P<Index>-?[0-9]+),POS=(?P<POS>-?[0-9]+),PTS=(?P<PTS>-?[0-9]+),"
            r"DTS=(?P<DTS>-?[0-9]+),EDI=(?P<EDI>-?[0-9]+)"
        )

        frame_second = re.compile(
            r"Key=(?P<Key>-?[0-9]+),Pic=(?P<Pic>-?[0-9]+),POC=(?P<POC>-?[0-9]+),"
            r"Repeat=(?P<Repeat>-?[0-9]+),Field=(?P<Field>-?[0-9]+)"
        )

        streaminfo = re.compile(
            r"Codec=(?P<Codec>[0-9]+),TimeBase=(?P<TimeBase>[0-9\/]+),Width=(?P<Width>[0-9]+),"
            r"Height=(?P<Height>[0-9]+),Format=(?P<Format>[0-9a-zA-Z]+),ColorSpace=(?P<ColorSpace>[0-9]+)"
        )

    class StreamInfo(NamedTuple):
        codec: int
        timebase: Fraction
        width: int
        height: int
        format: str
        colorspace: Matrix

    class Frame(NamedTuple):
        idx: int
        pos: int
        pts: int
        dts: int
        edi: int
        key: int
        pic: int
        poc: int
        repeat: int
        field: int

    @classmethod
    def from_file(
        cls, file: FilePathType, ref_or_length: int | vs.VideoNode | None = None, *, func: FuncExceptT | None = None
    ) -> LWIndex:
        func = func or cls.from_file

        file = Path(str(file)).resolve()

        length = ref_or_length.num_frames if isinstance(ref_or_length, vs.VideoNode) else ref_or_length  # type: ignore

        data = file.read_text('latin1').splitlines()

        indexstart, indexend = data.index("</StreamInfo>") + 1, data.index("</LibavReaderIndex>")

        if length and (idxlen := ((indexend - indexstart) // 2)) != length:
            raise FramesLengthError(
                func, '', 'index file length mismatch with specified length!',
                reason=dict(index=idxlen, clip=length)
            )

        sinfomatch = LWIndex.Regex.streaminfo.match(data[indexstart - 2])

        timebase_num, timebase_den = [
            int(i) for i in sinfomatch.group("TimeBase").split("/")  # type: ignore
        ]

        streaminfo = LWIndex.StreamInfo(
            int(sinfomatch.group("Codec")),  # type: ignore
            Fraction(timebase_num, timebase_den),
            int(sinfomatch.group("Width")),  # type: ignore
            int(sinfomatch.group("Height")),  # type: ignore
            sinfomatch.group("Format"),  # type: ignore
            Matrix(int(sinfomatch.group("ColorSpace"))),  # type: ignore
        )

        frames = sorted([
            LWIndex.Frame(*(
                int(x) for x in (
                    match[0].group(key) for match in [  # type: ignore
                        (LWIndex.Regex.frame_first.match(data[i]), ['Index', 'POS', 'PTS', 'DTS', 'EDI']),
                        (LWIndex.Regex.frame_second.match(data[i + 1]), ['Key', 'Pic', 'POC', 'Repeat', 'Field'])
                    ] for key in match[1]
                )
            ))
            for i in range(indexstart, indexend, 2)
        ], key=lambda x: x.pts)

        keyframes = Keyframes([i for i, f in enumerate(frames) if f.key], len(frames))

        return LWIndex(streaminfo, frames, keyframes)
