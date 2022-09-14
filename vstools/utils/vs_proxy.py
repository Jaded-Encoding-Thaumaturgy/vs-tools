from __future__ import annotations

import builtins
import weakref
from types import UnionType
from typing import TYPE_CHECKING, Any
from weakref import ReferenceType

import vapoursynth as vs
from vapoursynth import (
    AUDIO, BACK_CENTER, BACK_LEFT, BACK_RIGHT, CHROMA_BOTTOM, CHROMA_BOTTOM_LEFT, CHROMA_CENTER, CHROMA_LEFT,
    CHROMA_TOP, CHROMA_TOP_LEFT, FIELD_BOTTOM, FIELD_PROGRESSIVE, FIELD_TOP, FLOAT, FRONT_CENTER, FRONT_LEFT,
    FRONT_LEFT_OF_CENTER, FRONT_RIGHT, FRONT_RIGHT_OF_CENTER, GRAY, GRAY8, GRAY9, GRAY10, GRAY12, GRAY14, GRAY16,
    GRAY32, GRAYH, GRAYS, INTEGER, LOW_FREQUENCY, LOW_FREQUENCY2, MATRIX_BT470_BG, MATRIX_BT709, MATRIX_BT2020_CL,
    MATRIX_BT2020_NCL, MATRIX_CHROMATICITY_DERIVED_CL, MATRIX_CHROMATICITY_DERIVED_NCL, MATRIX_FCC, MATRIX_ICTCP,
    MATRIX_RGB, MATRIX_ST170_M, MATRIX_UNSPECIFIED, MATRIX_YCGCO, MESSAGE_TYPE_CRITICAL, MESSAGE_TYPE_DEBUG,
    MESSAGE_TYPE_FATAL, MESSAGE_TYPE_INFORMATION, MESSAGE_TYPE_WARNING, NONE, PRIMARIES_BT470_BG, PRIMARIES_BT470_M,
    PRIMARIES_BT709, PRIMARIES_BT2020, PRIMARIES_EBU3213_E, PRIMARIES_FILM, PRIMARIES_ST170_M, PRIMARIES_ST240_M,
    PRIMARIES_ST428, PRIMARIES_ST431_2, PRIMARIES_ST432_1, PRIMARIES_UNSPECIFIED, RANGE_FULL, RANGE_LIMITED, RGB, RGB24,
    RGB27, RGB30, RGB36, RGB42, RGB48, RGBH, RGBS, SIDE_LEFT, SIDE_RIGHT, STEREO_LEFT, STEREO_RIGHT,
    SURROUND_DIRECT_LEFT, SURROUND_DIRECT_RIGHT, TOP_BACK_CENTER, TOP_BACK_LEFT, TOP_BACK_RIGHT, TOP_CENTER,
    TOP_FRONT_CENTER, TOP_FRONT_LEFT, TOP_FRONT_RIGHT, TRANSFER_ARIB_B67, TRANSFER_BT470_BG, TRANSFER_BT470_M,
    TRANSFER_BT601, TRANSFER_BT709, TRANSFER_BT2020_10, TRANSFER_BT2020_12, TRANSFER_IEC_61966_2_1,
    TRANSFER_IEC_61966_2_4, TRANSFER_LINEAR, TRANSFER_LOG_100, TRANSFER_LOG_316, TRANSFER_ST240_M, TRANSFER_ST2084,
    TRANSFER_UNSPECIFIED, UNDEFINED, VIDEO, WIDE_LEFT, WIDE_RIGHT, YUV, YUV410P8, YUV411P8, YUV420P8, YUV420P9,
    YUV420P10, YUV420P12, YUV420P14, YUV420P16, YUV422P8, YUV422P9, YUV422P10, YUV422P12, YUV422P14, YUV422P16,
    YUV440P8, YUV444P8, YUV444P9, YUV444P10, YUV444P12, YUV444P14, YUV444P16, YUV444PH, YUV444PS, AudioChannels,
    AudioFrame, AudioNode, CallbackData, ChromaLocation, ColorFamily, ColorPrimaries, ColorRange, Core,
    CoreCreationFlags, Environment, EnvironmentData, EnvironmentPolicy, EnvironmentPolicyAPI, Error, FieldBased,
    FilterMode, FrameProps, FramePtr, Func, FuncData, Function, LogHandle, MatrixCoefficients, MediaType, MessageType,
    Plugin, PresetFormat, PythonVSScriptLoggingBridge, RawFrame, RawNode, SampleType, StandaloneEnvironmentPolicy,
    TransferCharacteristics, VideoFormat, VideoFrame, VideoNode, VideoOutputTuple, VSScriptEnvironmentPolicy,
    __api_version__, __pyx_capi__, __version__, _construct_parameter, _construct_type, _CoreProxy,
    ccfDisableAutoLoading, ccfDisableLibraryUnloading, ccfEnableGraphInspection, clear_output, clear_outputs,
    construct_signature, fmFrameState, fmParallel, fmParallelRequests, fmUnordered, get_current_environment, get_output,
    get_outputs, has_policy, register_policy
)

from ..exceptions import CustomRuntimeError

__all__ = [
    'AUDIO', 'BACK_CENTER', 'BACK_LEFT', 'BACK_RIGHT', 'CHROMA_BOTTOM', 'CHROMA_BOTTOM_LEFT', 'CHROMA_CENTER',
    'CHROMA_LEFT', 'CHROMA_TOP', 'CHROMA_TOP_LEFT', 'FIELD_BOTTOM', 'FIELD_PROGRESSIVE', 'FIELD_TOP', 'FLOAT',
    'FRONT_CENTER', 'FRONT_LEFT', 'FRONT_LEFT_OF_CENTER', 'FRONT_RIGHT', 'FRONT_RIGHT_OF_CENTER', 'GRAY', 'GRAY8',
    'GRAY9', 'GRAY10', 'GRAY12', 'GRAY14', 'GRAY16', 'GRAY32', 'GRAYH', 'GRAYS', 'INTEGER', 'LOW_FREQUENCY',
    'LOW_FREQUENCY2', 'MATRIX_BT470_BG', 'MATRIX_BT709', 'MATRIX_BT2020_CL', 'MATRIX_BT2020_NCL',
    'MATRIX_CHROMATICITY_DERIVED_CL', 'MATRIX_CHROMATICITY_DERIVED_NCL', 'MATRIX_FCC', 'MATRIX_ICTCP', 'MATRIX_RGB',
    'MATRIX_ST170_M', 'MATRIX_UNSPECIFIED', 'MATRIX_YCGCO', 'MESSAGE_TYPE_CRITICAL', 'MESSAGE_TYPE_DEBUG',
    'MESSAGE_TYPE_FATAL', 'MESSAGE_TYPE_INFORMATION', 'MESSAGE_TYPE_WARNING', 'NONE', 'PRIMARIES_BT470_BG',
    'PRIMARIES_BT470_M', 'PRIMARIES_BT709', 'PRIMARIES_BT2020', 'PRIMARIES_EBU3213_E', 'PRIMARIES_FILM',
    'PRIMARIES_ST170_M', 'PRIMARIES_ST240_M', 'PRIMARIES_ST428', 'PRIMARIES_ST431_2', 'PRIMARIES_ST432_1',
    'PRIMARIES_UNSPECIFIED', 'RANGE_FULL', 'RANGE_LIMITED', 'RGB', 'RGB24', 'RGB27', 'RGB30', 'RGB36', 'RGB42', 'RGB48',
    'RGBH', 'RGBS', 'SIDE_LEFT', 'SIDE_RIGHT', 'STEREO_LEFT', 'STEREO_RIGHT', 'SURROUND_DIRECT_LEFT',
    'SURROUND_DIRECT_RIGHT', 'TOP_BACK_CENTER', 'TOP_BACK_LEFT', 'TOP_BACK_RIGHT', 'TOP_CENTER', 'TOP_FRONT_CENTER',
    'TOP_FRONT_LEFT', 'TOP_FRONT_RIGHT', 'TRANSFER_ARIB_B67', 'TRANSFER_BT470_BG', 'TRANSFER_BT470_M', 'TRANSFER_BT601',
    'TRANSFER_BT709', 'TRANSFER_BT2020_10', 'TRANSFER_BT2020_12', 'TRANSFER_IEC_61966_2_1', 'TRANSFER_IEC_61966_2_4',
    'TRANSFER_LINEAR', 'TRANSFER_LOG_100', 'TRANSFER_LOG_316', 'TRANSFER_ST240_M', 'TRANSFER_ST2084',
    'TRANSFER_UNSPECIFIED', 'UNDEFINED', 'VIDEO', 'WIDE_LEFT', 'WIDE_RIGHT', 'YUV', 'YUV410P8', 'YUV411P8', 'YUV420P8',
    'YUV420P9', 'YUV420P10', 'YUV420P12', 'YUV420P14', 'YUV420P16', 'YUV422P8', 'YUV422P9', 'YUV422P10', 'YUV422P12',
    'YUV422P14', 'YUV422P16', 'YUV440P8', 'YUV444P8', 'YUV444P9', 'YUV444P10', 'YUV444P12', 'YUV444P14', 'YUV444P16',
    'YUV444PH', 'YUV444PS', 'AudioChannels', 'AudioFrame', 'AudioNode', 'CallbackData', 'ChromaLocation', 'ColorFamily',
    'ColorPrimaries', 'ColorRange', 'Core', 'CoreCreationFlags', 'Environment', 'EnvironmentData', 'EnvironmentPolicy',
    'EnvironmentPolicyAPI', 'Error', 'FieldBased', 'FilterMode', 'FrameProps', 'FramePtr', 'Func', 'FuncData',
    'Function', 'LogHandle', 'MatrixCoefficients', 'MediaType', 'MessageType', 'Plugin', 'PresetFormat',
    'PythonVSScriptLoggingBridge', 'RawFrame', 'RawNode', 'SampleType', 'StandaloneEnvironmentPolicy',
    'TransferCharacteristics', 'VideoFormat', 'VideoFrame', 'VideoNode', 'VideoOutputTuple',
    'VSScriptEnvironmentPolicy', '__api_version__', '__pyx_capi__', '__version__', '_construct_parameter',
    '_construct_type', '_CoreProxy', '_try_enable_introspection', 'ccfDisableAutoLoading', 'ccfDisableLibraryUnloading',
    'ccfEnableGraphInspection', 'clear_output', 'clear_outputs', 'construct_signature', 'core', 'fmFrameState',
    'fmParallel', 'fmParallelRequests', 'fmUnordered', 'get_current_environment', 'get_output', 'get_outputs',
    'has_policy', 'register_policy'
]

if not TYPE_CHECKING:
    from vapoursynth import _try_enable_introspection
    __all__.append('_try_enable_introspection')

if TYPE_CHECKING:
    class FunctionProxyBase(Function):
        ...

    class PluginProxyBase(Plugin):
        ...

    class CoreProxyBase(Core):
        def __init__(self) -> None:
            ...
else:
    FunctionProxyBase = PluginProxyBase = CoreProxyBase = object


class FunctionProxy(FunctionProxyBase):
    def __init__(self, plugin: PluginProxy, func_name: str) -> None:
        self.__dict__['func_ref'] = (plugin, func_name)

    def __getattr__(self, name: str) -> Function:
        function = proxy_utils.get_vs_function(self)

        return getattr(function, name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        function = proxy_utils.get_vs_function(self)

        return function(*args, **kwargs)


class PluginProxy(PluginProxyBase):
    def __init__(self, core: CoreProxy, namespace: str) -> None:
        self.__dict__['plugin_ref'] = (core, namespace)

    def __getattr__(self, name: str) -> Function:
        core, namespace = proxy_utils.get_core(self)
        vs_core = proxy_utils.get_vs_core(core)

        plugin = getattr(vs_core, namespace)

        if name in dir(plugin):
            return FunctionProxy(self, name)

        return getattr(plugin, name)


class CoreProxy(CoreProxyBase):
    def __init__(self, core: Core) -> None:
        self.__dict__['vs_core_ref'] = weakref.ref(core)

    def __getattr__(self, name: str) -> Plugin:
        core = proxy_utils.get_vs_core(self)

        if name in dir(core):
            return PluginProxy(self, name)

        return getattr(core, name)


class proxy_utils:
    @staticmethod
    def get_vs_core(core: CoreProxy) -> Core:
        vs_core_ref = core.__dict__['vs_core_ref']

        if (vs_core := vs_core_ref()) is None:
            raise CustomRuntimeError('The VapourSynth core has been freed!', CoreProxy)

        return vs_core

    @staticmethod
    def get_vs_function(func: FunctionProxy) -> Function:
        plugin, func_name = proxy_utils.get_plugin(func)
        core, namespace = proxy_utils.get_core(plugin)
        vs_core = proxy_utils.get_vs_core(core)

        return getattr(getattr(vs_core, namespace), func_name)

    @staticmethod
    def get_plugin(func: FunctionProxy) -> tuple[PluginProxy, str]:
        return func.__dict__['func_ref']

    @staticmethod
    def get_core(plugin: PluginProxy) -> tuple[CoreProxy, str]:
        return plugin.__dict__['plugin_ref']


builtins_isinstance = builtins.isinstance


def vstools_isinstance(
    __obj: object, __class_or_tuple: type | UnionType | tuple[type | UnionType | tuple[Any, ...], ...]
) -> bool:
    if __class_or_tuple in {_CoreProxy, Core} and builtins_isinstance(__obj, CoreProxy):
        return True

    return builtins_isinstance(__obj, __class_or_tuple)


builtins.isinstance = vstools_isinstance


def _get_core(self: VSCoreProxy) -> Core:
    core_ref: ReferenceType[Core] | None = object.__getattribute__(self, '_core')
    own_core: bool = object.__getattribute__(self, '_own_core')

    if core := (core_ref and core_ref()):
        return core

    if own_core:
        raise CustomRuntimeError(
            'The core the proxy made reference to was freed!', 'VSCoreProxy'
        )

    return vs.core.core


class VSCoreProxy(CoreProxyBase):
    def __init__(self, core: Core | None = None) -> None:
        self._own_core = core is not None
        self._core = core and weakref.ref(core)

    def __getattr__(self, name: str) -> Plugin:
        return getattr(_get_core(self), name)

    @property
    def core(self) -> Core:
        return _get_core(self)

    @property
    def proxied(self) -> CoreProxy:
        core = _get_core(self)

        if not hasattr(self, '_proxied'):
            self._proxied = out_core = CoreProxy(core)
        else:
            out_core = object.__getattribute__(self, '_proxied')

        return out_core


core = VSCoreProxy()
