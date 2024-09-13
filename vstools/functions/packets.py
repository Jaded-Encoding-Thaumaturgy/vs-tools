from __future__ import annotations

import io
import json
import shutil
import warnings
from subprocess import PIPE, Popen
from tempfile import NamedTemporaryFile
from typing import Self, TypedDict

import vapoursynth as vs
from stgpytools import CustomValueError, DependencyNotFoundError, FuncExceptT, SPath, SPathLike

from ..functions import Keyframes, PackageStorage
from ..utils import get_clip_filepath

__all__ = [
    'VideoPackets',
    'ScenePacketStats',
]


packets_storage = PackageStorage(package_name='packets')


class ScenePacketStats(TypedDict):
    pkt_scene_avg_size: float
    pkt_scene_max_size: float
    pkt_scene_min_size: float


class VideoPackets(list[int]):

    @classmethod
    def from_video(
        cls, src_file: SPathLike, out_file: SPathLike, offset: int = 0, *, func: FuncExceptT | None = None
    ) -> Self:
        func = func or cls.from_video

        if video_packets := cls.from_file(out_file, func=func):
            return video_packets

        out_file = packets_storage.get_file(out_file, ext='.txt')

        if not shutil.which('ffprobe'):
            raise DependencyNotFoundError(func, 'ffprobe', 'Could not find {package}! Make sure it\'s in your PATH!')

        proc = Popen([
            'ffprobe', '-hide_banner', '-show_frames', '-show_streams', '-threads', str(vs.core.num_threads),
            '-loglevel', 'quiet', '-print_format', 'json', '-select_streams', 'v:0', src_file
        ], stdout=PIPE)

        with NamedTemporaryFile('a+') as tempfile:
            assert proc.stdout

            for line in io.TextIOWrapper(proc.stdout, 'utf-8'):
                tempfile.write(line)

            data = dict(json.load(tempfile))

            frames = data.get('frames', {})

        if not frames:
            raise CustomValueError(f'No frames found in file, \'{src_file}\'! Your file may be corrupted!', func)

        pkt_sizes = [int(dict(frame).get('pkt_size', -1)) for frame in frames]

        print(f'Writing packet sizes to \'{out_file.absolute()}\'...')

        out_file.write_text('\n'.join(map(str, pkt_sizes)), 'utf-8', newline='\n')

        if offset < 0:
            pkt_sizes = [-1] * -offset + pkt_sizes
        elif offset > 0:
            pkt_sizes = pkt_sizes[offset:]

        return cls(pkt_sizes)

    @classmethod
    def from_file(cls, file: SPathLike, *, func: FuncExceptT | None = None) -> Self | None:
        if file is not None:
            file = packets_storage.get_file(file, ext='.txt')

            if file.exists() and not file.stat().st_size:
                file.unlink()

        if file is not None and file.exists():
            with file.open('r+') as f:
                return cls(map(int, f.readlines()))

        return None

    @classmethod
    def from_clip(
        cls, clip: vs.VideoNode,
        out_file: SPathLike, src_file: SPathLike | None = None,
        offset: int = 0, *, func: FuncExceptT | None = None
    ) -> Self:
        func = func or cls.from_video

        out_file = SPath(str(out_file)).stem + f'_{clip.num_frames}_{clip.fps_num}_{clip.fps_den}'

        if video_packets := cls.from_file(out_file, func=func):
            return video_packets

        src_file = get_clip_filepath(clip, src_file, func=func)

        return cls.from_video(src_file, out_file, offset, func=func)

    def get_scenestats(self, keyframes: Keyframes) -> list[ScenePacketStats]:
        stats = list[ScenePacketStats]()

        try:
            for start, end in zip(keyframes, keyframes[1:]):
                pkt_scenes = self[start:end]

                stats.append(
                    ScenePacketStats(
                        pkt_scene_avg_size=sum(pkt_scenes) / len(pkt_scenes),
                        pkt_scene_max_size=max(pkt_scenes),
                        pkt_scene_min_size=min(pkt_scenes)
                    )
                )
        except ValueError as e:
            raise CustomValueError('Some kind of error occurred!', self.get_scenestats, str(e))

        return stats

    def apply_props(
        self, clip: vs.VideoNode, keyframes: Keyframes | None = None, *, func: FuncExceptT | None = None
    ) -> vs.VideoNode:
        def _set_sizes_props(n: int) -> vs.VideoNode:
            if (pkt_size := self[n]) < 0:
                warnings.warn(f'{func}: \'Frame {n} bitrate could not be determined!\'')

            return clip.std.SetFrameProps(pkt_size=pkt_size)

        if not keyframes:
            return clip.std.FrameEval(_set_sizes_props)

        def _set_scene_stats(n: int) -> vs.VideoNode:
            if (pkt_size := self[n]) < 0:
                warnings.warn(f'{func}: \'Frame {n} bitrate could not be determined!\'')

            try:
                return clip.std.SetFrameProps(pkt_size=pkt_size, **scenestats[keyframes.scenes.indices[n]])
            except Exception:
                warnings.warn(f'{func}: \'Could not find stats for a section... (Frame: {n})\'')

                return clip.std.SetFrameProps(
                    pkt_size=-1,
                    pkt_scene_avg_size=-1,
                    pkt_scene_max_size=-1,
                    pkt_scene_min_size=-1
                )

        scenestats = self.get_scenestats(keyframes)

        return clip.std.FrameEval(_set_scene_stats)
