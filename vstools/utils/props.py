from __future__ import annotations

from typing import Any, TypeVar, overload

import vapoursynth as vs

from ..exceptions import FramePropError
from ..types import MISSING, BoundVSMapValue, HoldsPropValueT, MissingT

__all__ = [
    'get_prop',
    'merge_clip_props'
]

DT = TypeVar('DT')
CT = TypeVar('CT')


@overload
def get_prop(
    obj: HoldsPropValueT, key: str, t: type[BoundVSMapValue], cast: None = None, default: MissingT = MISSING
) -> BoundVSMapValue:
    ...


@overload
def get_prop(
    obj: HoldsPropValueT, key: str, t: type[BoundVSMapValue], cast: type[CT], default: MissingT = MISSING
) -> CT:
    ...


@overload
def get_prop(
    obj: HoldsPropValueT, key: str, t: type[BoundVSMapValue], cast: None = None, default: DT | MissingT = MISSING
) -> BoundVSMapValue | DT:
    ...


@overload
def get_prop(
    obj: HoldsPropValueT, key: str, t: type[BoundVSMapValue], cast: type[CT], default: DT | MissingT = MISSING
) -> CT | DT:
    ...


def get_prop(
    obj: HoldsPropValueT, key: str, t: type[BoundVSMapValue],
    cast: type[CT] | None = None, default: DT | MissingT = MISSING
) -> BoundVSMapValue | CT | DT:
    """
    Get FrameProp ``prop`` from frame ``frame`` with expected type ``t`` to satisfy the type checker.
    :param frame:               Frame containing props.
    :param key:                 Prop to get.
    :param t:                   type of prop.
    :param cast:                Cast value to this type, if specified.
    :param default:             Fallback value.
    :return:                    frame.prop[key].
    :raises FramePropError:     ``key`` is not found in props.
    :raises FramePropError:     Returns a prop of the wrong type.
    """

    if isinstance(obj, (vs.VideoNode, vs.AudioNode)):
        props = obj.get_frame(0).props
    elif isinstance(obj, (vs.VideoFrame, vs.AudioFrame)):
        props = obj.props
    else:
        props = obj

    prop: Any = MISSING

    try:
        prop = props[key]

        if not isinstance(prop, t):
            raise TypeError

        if cast is None:
            return prop

        return cast(prop)  # type: ignore
    except BaseException as e:
        if not isinstance(default, MissingT):
            return default

        if isinstance(e, KeyError) or prop is MISSING:
            e = FramePropError(get_prop, key, 'Key {key} not present in props!')
        elif isinstance(e, TypeError):
            e = FramePropError(
                get_prop, key, 'Key {key} did not contain expected type: Expected {t} got {prop_t}!',
                t=t, prop_t=type(prop)
            )
        else:
            e = FramePropError(get_prop, key)

        raise e


def merge_clip_props(*clips: vs.VideoNode, main_idx: int = 0) -> vs.VideoNode:
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
