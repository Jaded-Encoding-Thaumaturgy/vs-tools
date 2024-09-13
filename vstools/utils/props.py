from __future__ import annotations

from typing import Any, Callable, TypeVar, overload

import vapoursynth as vs
from stgpytools import MISSING, FileWasNotFoundError, FuncExceptT, MissingT, SPath, SPathLike, SupportsString

from ..enums import PropEnum
from ..exceptions import FramePropError
from ..types import BoundVSMapValue, HoldsPropValueT

__all__ = [
    'get_prop',
    'merge_clip_props',
    'get_clip_filepath'
]

DT = TypeVar('DT')
CT = TypeVar('CT')


@overload
def get_prop(
    obj: HoldsPropValueT, key: SupportsString | PropEnum, t: type[BoundVSMapValue],
    cast: None = None, default: MissingT = MISSING, func: FuncExceptT | None = None  # type: ignore
) -> BoundVSMapValue:
    ...


@overload
def get_prop(
    obj: HoldsPropValueT, key: SupportsString | PropEnum, t: type[BoundVSMapValue],
    cast: type[CT], default: MissingT = MISSING, func: FuncExceptT | None = None  # type: ignore
) -> CT:
    ...


@overload
def get_prop(
    obj: HoldsPropValueT, key: SupportsString | PropEnum, t: type[BoundVSMapValue],
    cast: None = None, default: DT | MissingT = MISSING,
    func: FuncExceptT | None = None
) -> BoundVSMapValue | DT:
    ...


@overload
def get_prop(
    obj: HoldsPropValueT, key: SupportsString | PropEnum, t: type[BoundVSMapValue],
    cast: type[CT] | Callable[[BoundVSMapValue], CT], default: DT | MissingT = MISSING,
    func: FuncExceptT | None = None
) -> CT | DT:
    ...


def get_prop(
    obj: HoldsPropValueT, key: SupportsString | PropEnum, t: type[BoundVSMapValue],
    cast: type[CT] | Callable[[BoundVSMapValue], CT] | None = None, default: DT | MissingT = MISSING,
    func: FuncExceptT | None = None
) -> BoundVSMapValue | CT | DT:
    """
    Get FrameProp ``prop`` from frame ``frame`` with expected type ``t`` to satisfy the type checker.

    :param obj:                 Clip or frame containing props.
    :param key:                 Prop to get.
    :param t:                   type of prop.
    :param cast:                Cast value to this type, if specified.
    :param default:             Fallback value.

    :return:                    frame.prop[key].

    :raises FramePropError:     ``key`` is not found in props.
    :raises FramePropError:     Returns a prop of the wrong type.
    """

    from ..functions import fallback

    if isinstance(obj, vs.RawFrame):
        props = obj.props  # type: ignore
    elif isinstance(obj, vs.RawNode):
        props = obj.get_frame(0).props  # type: ignore
    else:
        props = obj

    prop: Any = MISSING

    try:
        try:
            prop = props[key]  # type: ignore
        except Exception:
            if isinstance(key, type) and issubclass(key, PropEnum):
                key = key.prop_key
            else:
                key = str(key)

            prop = props[key]  # type: ignore

        if not isinstance(prop, t):
            if issubclass(t, str) and isinstance(prop, bytes):
                return prop.decode('utf-8')
            raise TypeError

        if cast is None:
            return prop

        return cast(prop)  # type: ignore
    except BaseException as e:
        if default is not MISSING:
            return default

        func: FuncExceptT = fallback(func, get_prop)  # type: ignore

        if isinstance(e, KeyError) or prop is MISSING:
            e = FramePropError(func, key, 'Key {key} not present in props!')  # type: ignore
        elif isinstance(e, TypeError):
            e = FramePropError(
                func, key, 'Key {key} did not contain expected type: Expected {t} got {prop_t}!',  # type: ignore
                t=t, prop_t=type(prop)
            )
        else:
            e = FramePropError(func, key)  # type: ignore

        raise e


def merge_clip_props(*clips: vs.VideoNode, main_idx: int = 0) -> vs.VideoNode:
    """
    Merge frame properties from all provided clips.

    The props of the main clip (defined by main_idx) will be overwritten,
    and all other props will be added to it.

    :param clips:       Clips which will be merged.
    :param main_idx:    Index of the main clip to which all other clips props will be merged.

    :return:            First clip with all the frameprops of every other given clip merged into it.
    """

    if len(clips) == 1:
        return clips[0]

    def _merge_props(f: list[vs.VideoFrame], n: int) -> vs.VideoFrame:
        fdst = f[main_idx].copy()

        for i, frame in enumerate(f):
            if i == main_idx:
                continue

            fdst.props.update(frame.props)

        return fdst

    return clips[0].std.ModifyFrame(clips, _merge_props)


@overload
def get_clip_filepath(
    clip: vs.VideoNode, fallback: SPathLike | None = ..., strict: bool = True, *, func: FuncExceptT | None = ...
) -> SPath:
    ...


@overload
def get_clip_filepath(  # type:ignore[misc]
    clip: vs.VideoNode, fallback: SPathLike | None = ..., strict: bool = False, *, func: FuncExceptT | None = ...
) -> SPath | None:
    ...


def get_clip_filepath(
    clip: vs.VideoNode, fallback: SPathLike | None = None, strict: bool = False, *, func: FuncExceptT | None = None
) -> SPath | None:
    """
    Helper function to get the file path from a clip.

    This function also checks to ensure the file exists,
    and throws an error if it doesn't.

    :param clip:                    The clip to get the file path from.
    :param fallback:                Fallback file path to use if the `prop` is not found.
    :param strict:                  If True, will raise an error if the `prop` is not found.
                                    This makes it so the function will NEVER return False.
                                    Default: False.
    :param func:                    Function returned for error handling.
                                    This should only be set by VS package developers.

    :raises FileWasNotFoundError:   The file path was not found.
    :raises FramePropError:         The property was not found in the clip.
    """

    func = func or get_clip_filepath

    if fallback is not None and not (fallback_path := SPath(fallback)).exists() and strict:
        raise FileWasNotFoundError('Fallback file not found!', func, fallback_path.absolute())

    if not (path := get_prop(clip, 'idx_filepath', str, default=MISSING if strict else False, func=func)):
        return fallback_path or None

    if not (spath := SPath(str(path))).exists() and not fallback:
        raise FileWasNotFoundError('File not found!', func, spath.absolute())

    if spath.exists():
        return spath

    if fallback is not None and fallback_path.exists():
        return fallback_path

    raise FileWasNotFoundError('File not found!', func, spath.absolute())
