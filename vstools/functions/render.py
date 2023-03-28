from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import floor
from typing import BinaryIO, Callable, Literal, overload

import vapoursynth as vs

from ..exceptions import CustomRuntimeError, CustomValueError, InvalidColorFamilyError
from ..types import T
from .progress import get_render_progress

__all__ = [
    'AsyncRenderConf',

    'clip_async_render'
]


@dataclass
class AsyncRenderConf:
    n: int = 2
    one_pix_frame: bool = False
    parallel_input: bool = False


@overload
def clip_async_render(  # type: ignore
    clip: vs.VideoNode, outfile: BinaryIO | None = None, progress: str | None = None,
    callback: None = None, prefetch: int = 0, backlog: int = -1, y4m: bool = False,
    async_requests: int | bool | AsyncRenderConf = False
) -> None:
    ...


@overload
def clip_async_render(
    clip: vs.VideoNode, outfile: BinaryIO | None = None, progress: str | None = None,
    callback: Callable[[int, vs.VideoFrame], T] = ..., prefetch: int = 0,
    backlog: int = -1, y4m: bool = False, async_requests: int | bool | AsyncRenderConf = False
) -> list[T]:
    ...


def clip_async_render(
    clip: vs.VideoNode, outfile: BinaryIO | None = None, progress: str | None = None,
    callback: Callable[[int, vs.VideoFrame], T] | None = None, prefetch: int = 0,
    backlog: int = -1, y4m: bool | None = None, async_requests: int | bool | AsyncRenderConf = False
) -> list[T] | None:
    from .funcs import fallback

    result = dict[int, T]()

    async_conf: AsyncRenderConf | Literal[False]
    if async_requests is True:
        async_conf = AsyncRenderConf(1)
    elif isinstance(async_requests, int):
        if isinstance(async_requests, int) and async_requests <= 1:
            async_conf = False
        else:
            async_conf = AsyncRenderConf(async_requests)
    else:
        async_conf = async_requests

    if async_conf and async_conf.one_pix_frame and y4m:
        raise CustomValueError('You cannot have y4m=True and one_pix_frame in AsyncRenderConf!')

    pr_update: Callable[[], None]

    if callback:
        def get_callback(shift: int = 0) -> Callable[[int, vs.VideoFrame], vs.VideoFrame]:
            if shift:
                if outfile is None and progress is not None:
                    def _cb(n: int, f: vs.VideoFrame) -> vs.VideoFrame:
                        n += shift
                        result[n] = callback(n, f)  # type: ignore[misc]
                        pr_update()
                        return f
                else:
                    def _cb(n: int, f: vs.VideoFrame) -> vs.VideoFrame:
                        n += shift
                        result[n] = callback(n, f)  # type: ignore[misc]
                        return f
            else:
                if outfile is None and progress is not None:
                    def _cb(n: int, f: vs.VideoFrame) -> vs.VideoFrame:
                        result[n] = callback(n, f)  # type: ignore[misc]
                        pr_update()
                        return f
                else:
                    def _cb(n: int, f: vs.VideoFrame) -> vs.VideoFrame:
                        result[n] = callback(n, f)  # type: ignore[misc]
                        return f

            return _cb

        if async_conf and async_conf.one_pix_frame and (clip.width != clip.height != 1):
            clip = clip.std.CropAbs(1, 1)

        if not async_conf or async_conf.n == 1:
            blankclip = clip.std.BlankClip(keep=True)

            _cb = get_callback()

            if async_conf:
                rend_clip = blankclip.std.FrameEval(lambda n: blankclip.std.ModifyFrame(clip, _cb))
            else:
                rend_clip = blankclip.std.ModifyFrame(clip, _cb)
        else:
            if outfile:
                raise CustomValueError('You cannot have and output file with multi async request!')

            chunk = floor(clip.num_frames / async_conf.n)
            cl = chunk * async_conf.n

            blankclip = clip.std.BlankClip(length=chunk, keep=True)

            stack = async_conf.parallel_input and not async_conf.one_pix_frame

            if stack:
                rend_clip = vs.core.std.StackHorizontal([
                    blankclip.std.ModifyFrame(clip[chunk * i:chunk * (i + 1)], get_callback(chunk * i))
                    for i in range(async_conf.n)
                ])
            else:
                _cb = get_callback()

                clip_indices = list(range(cl))
                range_indices = list(range(async_conf.n))

                indices = [clip_indices[i::async_conf.n] for i in range_indices]

                def _var(n: int, f: list[vs.VideoFrame]) -> vs.VideoFrame:
                    for i, fi in zip(range_indices, f):
                        _cb(indices[i][n], fi)

                    return f[0]

                rend_clip = blankclip.std.ModifyFrame([clip[i::async_conf.n] for i in range_indices], _var)

            if cl != clip.num_frames:
                rend_rest = blankclip[:clip.num_frames - cl].std.ModifyFrame(clip[cl:], get_callback(cl))
                rend_clip = vs.core.std.Splice([rend_clip, rend_rest], stack)
    else:
        rend_clip = clip

    if outfile is None:
        if y4m:
            raise CustomValueError('You cannot have y4m=False without any output file!')

        clip_it = rend_clip.frames(prefetch, backlog, True)

        if progress is None:
            deque(clip_it, 0)
        else:
            with get_render_progress(progress, clip.num_frames) as pr:
                if callback:
                    pr_update = pr.update
                    deque(clip_it, 0)
                else:
                    for _ in clip_it:
                        pr.update()
    else:
        y4m = fallback(y4m, bool(rend_clip.format and (rend_clip.format.color_family is vs.YUV)))

        if y4m:
            if rend_clip.format is None:
                raise CustomValueError('You cannot have y4m=True when rendering a variable resolution clip!')
            else:
                InvalidColorFamilyError.check(
                    rend_clip, (vs.YUV, vs.GRAY), clip_async_render,
                    message='Can only render to y4m clips with {correct} color family, not {wrong}!'
                )

        if progress is None:
            rend_clip.output(outfile, y4m, None, prefetch, backlog)
        else:
            with get_render_progress(progress, clip.num_frames) as pr:
                rend_clip.output(outfile, y4m, pr.update, prefetch, backlog)

    if callback:
        try:
            return [result[i] for i in range(clip.num_frames)]
        except KeyError:
            raise CustomRuntimeError('There was an error with the rendering and one frame request was rejected!')

    return None
