from __future__ import annotations

from fractions import Fraction
from json import JSONDecoder
from pathlib import Path
from shutil import which
from subprocess import PIPE, run
from typing import Any, Literal, overload

from ..exceptions import CustomRuntimeError, CustomValueError
from ..types import FuncExceptT, inject_self
from .file import check_perms
from .mime import FileType


__all__ = [
    'FFProbe',

    'FFProbeStream',

    'FFProbeVideoStream',
    'FFProbeStreamSideData',

    'FFProbeAudioStream'
]


class FFProbeStreamSideData:
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    side_data_type: str
    displaymatrix: str  #
    rotation: int  #


# TODO
class FFProbeObjectBase:
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    def __init__(self, ffmpeg_obj: dict[str, Any]) -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

        for key, value in ffmpeg_obj.items():
            setattr(self, key, value)


class FFProbeStreamBase(FFProbeObjectBase):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    index: int
    codec_name: str
    codec_long_name: str
    profile: str
    codec_type: FileType
    codec_time_base: Fraction
    codec_tag_string: str
    codec_tag: int
    r_frame_rate: Fraction
    avg_frame_rate: Fraction
    time_base: Fraction
    start_pts: int
    start_time: float
    disposition: dict[str, str]
    tags: dict[str, str]


class FFProbeStream(FFProbeStreamBase):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    duration_ts: int | None
    duration: float | None
    bit_rate: int | None
    max_bit_rate: int | None
    nb_frames: int | None
    nb_read_frames: int | None
    side_data_list: list[FFProbeStreamSideData] | None


class FFProbeStreamSafe(FFProbeStream):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    duration_ts: int
    duration: float
    bit_rate: int
    max_bit_rate: int
    nb_frames: int
    nb_read_frames: int
    side_data_list: list[FFProbeStreamSideData]


class FFProbeVideoStreamBase(FFProbeStreamBase):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    codec_type: Literal[FileType.VIDEO]
    width: int
    height: int
    coded_width: int
    coded_height: int
    closed_captions: int
    has_b_frames: int
    sample_aspect_ratio: Fraction
    display_aspect_ratio: Fraction
    pix_fmt: str
    level: int
    color_range: str
    refs: int


class FFProbeVideoStream(FFProbeStream, FFProbeVideoStreamBase):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    color_space: str | None
    color_transfer: str | None
    color_primaries: str | None
    chroma_location: str | None
    field_order: str | None
    is_avc: bool | None
    nal_length_size: int | None
    bits_per_raw_sample: int | None


class FFProbeVideoStreamSafe(FFProbeStreamSafe, FFProbeVideoStreamBase):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    color_space: str
    color_transfer: str
    color_primaries: str
    chroma_location: str
    field_order: str
    is_avc: bool
    nal_length_size: int
    bits_per_raw_sample: int


class FFProbeAudioStream(FFProbeStream):
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    sample_fmt: str
    sample_rate: int
    channels: int
    channel_layout: str
    bits_per_sample: int


class FFProbe:
    """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

    class FFProbeNotFoundError(CustomRuntimeError):
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""

        ...

    json_decoder: JSONDecoder

    def __init__(self, *, func: FuncExceptT | None = None, bin_path: str | Path = 'ffprobe') -> None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        self.bin_path = Path(bin_path)

        if not which(str(self.bin_path)):
            raise FFProbe.FFProbeNotFoundError('FFprobe was not found!')

        self.json_decoder = JSONDecoder(
            object_pairs_hook=None,
            object_hook=None,
            parse_constant=None,
            parse_float=None,
            parse_int=None,
            strict=True
        )

    @overload
    def _get_stream(  # type: ignore
        self, filename: str | Path, file_type: FileType | None = FileType.VIDEO,
        *, index: int = 0, func: FuncExceptT | None = None
    ) -> FFProbeStream | None:
        ...

    @overload
    def _get_stream(
        self, filename: str | Path, file_type: FileType | None = FileType.VIDEO,
        *, index: None = None, func: FuncExceptT | None = None
    ) -> list[FFProbeStream] | None:
        ...

    def _get_stream(
        self, filename: str | Path, file_type: FileType | None = FileType.VIDEO,
        *, index: int | None = 0, func: FuncExceptT | None = None
    ) -> FFProbeStream | list[FFProbeStream] | None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        check_perms(filename, 'r', func=func)

        if index is not None and index < 0:
            raise CustomValueError('Stream index must be positive!', func)

        if file_type is None:
            select_streams = tuple[str]()
        else:
            idx_str = '' if index is None else f':{index}'
            select_streams = ('-select_streams', f'{file_type[0]}{idx_str}')

        ffprobe_output = run([
            str(self.bin_path), str(filename),
            *select_streams,
            '-show_streams',
            '-print_format', 'json',
            '-loglevel', 'panic'
        ], stdout=PIPE, check=True, encoding='utf-8')

        if ffprobe_output.stderr:
            raise CustomRuntimeError(ffprobe_output.stderr, func)

        ffprobe_data = self.json_decoder.decode(ffprobe_output.stdout)

        if 'streams' not in ffprobe_data or not ffprobe_data['streams']:
            return None

        ffprobe_streams: list[dict[str, Any]] = ffprobe_data['streams']

        ffprobe_obj_type = FFProbeStream

        if file_type is FileType.VIDEO:
            ffprobe_obj_type = FFProbeVideoStream
        elif file_type is FileType.AUDIO:
            ffprobe_obj_type = FFProbeAudioStream

        if index is None:
            return [ffprobe_obj_type(obj) for obj in ffprobe_streams]

        return ffprobe_obj_type(ffprobe_streams[index])

    @inject_self
    def get_stream(
        self, filename: str | Path, file_type: FileType | None,
        *, index: int = 0, func: FuncExceptT | None = None
    ) -> FFProbeStream | None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        return self._get_stream(filename, file_type, index=index, func=func or self.get_stream)

    @inject_self
    def get_streams(
        self, filename: str | Path, file_type: FileType | None,
        *, func: FuncExceptT | None = None
    ) -> list[FFProbeStream] | None:
        """@@PLACEHOLDER@@ PLEASE REPORT THIS IF YOU SEE THIS"""
        return self._get_stream(filename, file_type, index=None, func=self.get_streams if func is None else func)