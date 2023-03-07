from __future__ import annotations

from collections import deque
from math import floor
from typing import BinaryIO, Callable, overload

import vapoursynth as vs

from ..exceptions import CustomRuntimeError, CustomValueError, InvalidColorFamilyError
from ..types import T
from .progress import get_render_progress


@overload
def clip_async_render(  # type: ignore
    clip: vs.VideoNode, outfile: BinaryIO | None = None, progress: str | None = None,
    callback: None = None, prefetch: int = 0, backlog: int = -1, y4m: bool = False,
    async_requests: int | bool = False
) -> None:
    ...


@overload
def clip_async_render(
    clip: vs.VideoNode, outfile: BinaryIO | None = None, progress: str | None = None,
    callback: Callable[[int, vs.VideoFrame], T] = ..., prefetch: int = 0,
    backlog: int = -1, y4m: bool = False, async_requests: int | bool = False
) -> list[T]:
    ...


def clip_async_render(
    clip: vs.VideoNode, outfile: BinaryIO | None = None, progress: str | None = None,
    callback: Callable[[int, vs.VideoFrame], T] | None = None, prefetch: int = 0,
    backlog: int = -1, y4m: bool | None = None, async_requests: int | bool = False
) -> list[T] | None:
    from .funcs import fallback

    result = dict[int, T]()

    pr_update: Callable[[], None]

    if callback:
        def get_callback(shift: int = 0) -> Callable[[int, vs.VideoFrame], vs.VideoFrame]:
            if shift:
                if outfile is None and progress is not None:
                    def _cb(n: int, f: vs.VideoFrame) -> vs.VideoFrame:
                        result[n] = callback(n + shift, f)  # type: ignore[misc]
                        pr_update()
                        return f
                else:
                    def _cb(n: int, f: vs.VideoFrame) -> vs.VideoFrame:
                        result[n] = callback(n + shift, f)  # type: ignore[misc]
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

        if isinstance(async_requests, bool):
            blankclip = clip.std.BlankClip(keep=True)

            _cb = get_callback()

            if async_requests:
                rend_clip = blankclip.std.FrameEval(lambda n: blankclip.std.ModifyFrame(clip, _cb))
            else:
                rend_clip = blankclip.std.ModifyFrame(clip, _cb)
        else:
            if outfile:
                raise CustomValueError('You cannot have and output file with multi async request!')

            chunk = floor(clip.num_frames / async_requests)

            blankclip = clip.std.BlankClip(length=chunk, keep=True)

            rend_clip = vs.core.std.StackHorizontal([
                blankclip.std.ModifyFrame(clip[chunk * i:chunk * (i + 1)], get_callback(chunk * i))
                for i in range(async_requests)
            ])

            if (cl := (chunk * async_requests)) != clip.num_frames:
                rend_clip = vs.core.std.Splice([rend_clip, clip[cl + 1:]], True)
    else:
        rend_clip = clip

    if outfile is None:
        if y4m:
            raise CustomValueError('You cannot have y4m=False without any output file!')

        clip_it = rend_clip.frames(prefetch, backlog, True)

        if progress is None:
            deque(clip_it, 0)
        else:
            with get_render_progress(progress, rend_clip.num_frames) as pr:
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
            with get_render_progress(progress, rend_clip.num_frames) as pr:
                rend_clip.output(outfile, y4m, pr.update, prefetch, backlog)

    if callback:
        try:
            return [result[i] for i in range(rend_clip.num_frames)]
        except KeyError:
            raise CustomRuntimeError('There was an error with the rendering and one frame request was rejected!')

    return None
