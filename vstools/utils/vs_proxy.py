from __future__ import annotations

import builtins
import weakref
from ctypes import Structure
from inspect import Parameter
from logging import NOTSET as LogLevelUnset
from logging import Handler, LogRecord
from types import UnionType
from typing import TYPE_CHECKING, Any, Callable, NoReturn
from weakref import ReferenceType

import vapoursynth as vs
from vapoursynth import (
    AUDIO, BACK_CENTER, BACK_LEFT, BACK_RIGHT, CHROMA_BOTTOM, CHROMA_BOTTOM_LEFT, CHROMA_CENTER, CHROMA_LEFT,
    CHROMA_TOP, CHROMA_TOP_LEFT, FIELD_BOTTOM, FIELD_PROGRESSIVE, FIELD_TOP, FLOAT, FRONT_CENTER, FRONT_LEFT,
    FRONT_LEFT_OF_CENTER, FRONT_RIGHT, FRONT_RIGHT_OF_CENTER, GRAY, INTEGER, LOW_FREQUENCY, LOW_FREQUENCY2,
    MATRIX_BT470_BG, MATRIX_BT709, MATRIX_BT2020_CL, MATRIX_BT2020_NCL, MATRIX_CHROMATICITY_DERIVED_CL,
    MATRIX_CHROMATICITY_DERIVED_NCL, MATRIX_FCC, MATRIX_ICTCP, MATRIX_RGB, MATRIX_ST170_M, MATRIX_UNSPECIFIED,
    MATRIX_YCGCO, MESSAGE_TYPE_CRITICAL, MESSAGE_TYPE_DEBUG, MESSAGE_TYPE_FATAL, MESSAGE_TYPE_INFORMATION,
    MESSAGE_TYPE_WARNING, NONE, PRIMARIES_BT470_BG, PRIMARIES_BT470_M, PRIMARIES_BT709, PRIMARIES_BT2020,
    PRIMARIES_EBU3213_E, PRIMARIES_FILM, PRIMARIES_ST170_M, PRIMARIES_ST240_M, PRIMARIES_ST428, PRIMARIES_ST431_2,
    PRIMARIES_ST432_1, PRIMARIES_UNSPECIFIED, RANGE_FULL, RANGE_LIMITED, RGB, SIDE_LEFT, SIDE_RIGHT, STEREO_LEFT,
    STEREO_RIGHT, SURROUND_DIRECT_LEFT, SURROUND_DIRECT_RIGHT, TOP_BACK_CENTER, TOP_BACK_LEFT, TOP_BACK_RIGHT,
    TOP_CENTER, TOP_FRONT_CENTER, TOP_FRONT_LEFT, TOP_FRONT_RIGHT, TRANSFER_ARIB_B67, TRANSFER_BT470_BG,
    TRANSFER_BT470_M, TRANSFER_BT601, TRANSFER_BT709, TRANSFER_BT2020_10, TRANSFER_BT2020_12, TRANSFER_IEC_61966_2_1,
    TRANSFER_IEC_61966_2_4, TRANSFER_LINEAR, TRANSFER_LOG_100, TRANSFER_LOG_316, TRANSFER_ST240_M, TRANSFER_ST2084,
    TRANSFER_UNSPECIFIED, UNDEFINED, VIDEO, WIDE_LEFT, WIDE_RIGHT, YUV, AudioChannels, AudioFrame, AudioNode,
    ChromaLocation, ColorFamily, ColorPrimaries, ColorRange, Core, CoreCreationFlags, Environment, EnvironmentData,
    EnvironmentPolicy, EnvironmentPolicyAPI, Error, FieldBased, FilterMode, FrameProps, FramePtr, Func, FuncData,
    Function, LogHandle, MatrixCoefficients, MediaType, MessageType, Plugin
)
from vapoursynth import PresetFormat as VSPresetFormat
from vapoursynth import (
    RawFrame, RawNode, SampleType, TransferCharacteristics, VideoFormat, VideoFrame, VideoNode, VideoOutputTuple,
    __api_version__, __version__, _CoreProxy, ccfDisableAutoLoading, ccfDisableLibraryUnloading,
    ccfEnableGraphInspection, clear_output, clear_outputs, construct_signature, fmFrameState, fmParallel,
    fmParallelRequests, fmUnordered, get_current_environment, get_output, get_outputs, has_policy, register_policy
)

from ..exceptions import CustomRuntimeError
from .vs_enums import (
    GRAY8, GRAY9, GRAY10, GRAY11, GRAY12, GRAY13, GRAY14, GRAY15, GRAY16, GRAY17, GRAY18, GRAY19, GRAY20, GRAY21,
    GRAY22, GRAY23, GRAY24, GRAY25, GRAY26, GRAY27, GRAY28, GRAY29, GRAY30, GRAY31, GRAY32, GRAYH, GRAYS, RGB24, RGB27,
    RGB30, RGB33, RGB36, RGB39, RGB42, RGB45, RGB48, RGB51, RGB54, RGB57, RGB60, RGB63, RGB66, RGB69, RGB72, RGB75,
    RGB78, RGB81, RGB84, RGB87, RGB90, RGB93, RGB96, RGBH, RGBS, YUV410P8, YUV410P9, YUV410P10, YUV410P11, YUV410P12,
    YUV410P13, YUV410P14, YUV410P15, YUV410P16, YUV410P17, YUV410P18, YUV410P19, YUV410P20, YUV410P21, YUV410P22,
    YUV410P23, YUV410P24, YUV410P25, YUV410P26, YUV410P27, YUV410P28, YUV410P29, YUV410P30, YUV410P31, YUV410P32,
    YUV410PH, YUV410PS, YUV411P8, YUV411P9, YUV411P10, YUV411P11, YUV411P12, YUV411P13, YUV411P14, YUV411P15, YUV411P16,
    YUV411P17, YUV411P18, YUV411P19, YUV411P20, YUV411P21, YUV411P22, YUV411P23, YUV411P24, YUV411P25, YUV411P26,
    YUV411P27, YUV411P28, YUV411P29, YUV411P30, YUV411P31, YUV411P32, YUV411PH, YUV411PS, YUV420P8, YUV420P9, YUV420P10,
    YUV420P11, YUV420P12, YUV420P13, YUV420P15, YUV420P16, YUV420P17, YUV420P18, YUV420P19, YUV420P20, YUV420P21,
    YUV420P22, YUV420P23, YUV420P24, YUV420P25, YUV420P26, YUV420P27, YUV420P28, YUV420P29, YUV420P30, YUV420P31,
    YUV420P32, YUV420PH, YUV420PS, YUV422P8, YUV422P9, YUV422P10, YUV422P11, YUV422P12, YUV422P13, YUV422P14, YUV422P15,
    YUV422P16, YUV422P17, YUV422P18, YUV422P19, YUV422P20, YUV422P21, YUV422P22, YUV422P23, YUV422P24, YUV422P25,
    YUV422P26, YUV422P27, YUV422P28, YUV422P29, YUV422P30, YUV422P31, YUV422P32, YUV422PH, YUV422PS, YUV440P8, YUV440P9,
    YUV440P10, YUV440P11, YUV440P12, YUV440P13, YUV440P14, YUV440P15, YUV440P16, YUV440P17, YUV440P18, YUV440P19,
    YUV440P20, YUV440P21, YUV440P22, YUV440P23, YUV440P24, YUV440P25, YUV440P26, YUV440P27, YUV440P28, YUV440P29,
    YUV440P30, YUV440P31, YUV440P32, YUV440PH, YUV440PS, YUV444P8, YUV444P9, YUV444P10, YUV444P11, YUV444P12, YUV444P13,
    YUV444P14, YUV444P15, YUV444P16, YUV444P17, YUV444P18, YUV444P19, YUV444P20, YUV444P21, YUV444P22, YUV444P23,
    YUV444P24, YUV444P25, YUV444P26, YUV444P27, YUV444P28, YUV444P29, YUV444P30, YUV444P31, YUV444P32, YUV444PH,
    YUV444PS, PresetFormat
)

__all__ = [
    'AUDIO', 'BACK_CENTER', 'BACK_LEFT', 'BACK_RIGHT', 'CHROMA_BOTTOM', 'CHROMA_BOTTOM_LEFT', 'CHROMA_CENTER',
    'CHROMA_LEFT', 'CHROMA_TOP', 'CHROMA_TOP_LEFT', 'FIELD_BOTTOM', 'FIELD_PROGRESSIVE', 'FIELD_TOP', 'FLOAT',
    'FRONT_CENTER', 'FRONT_LEFT', 'FRONT_LEFT_OF_CENTER', 'FRONT_RIGHT', 'FRONT_RIGHT_OF_CENTER', 'GRAY', 'INTEGER',
    'LOW_FREQUENCY', 'LOW_FREQUENCY2', 'MATRIX_BT470_BG', 'MATRIX_BT709', 'MATRIX_BT2020_CL', 'MATRIX_BT2020_NCL',
    'MATRIX_CHROMATICITY_DERIVED_CL', 'MATRIX_CHROMATICITY_DERIVED_NCL', 'MATRIX_FCC', 'MATRIX_ICTCP', 'MATRIX_RGB',
    'MATRIX_ST170_M', 'MATRIX_UNSPECIFIED', 'MATRIX_YCGCO', 'MESSAGE_TYPE_CRITICAL', 'MESSAGE_TYPE_DEBUG',
    'MESSAGE_TYPE_FATAL', 'MESSAGE_TYPE_INFORMATION', 'MESSAGE_TYPE_WARNING', 'NONE', 'PRIMARIES_BT470_BG',
    'PRIMARIES_BT470_M', 'PRIMARIES_BT709', 'PRIMARIES_BT2020', 'PRIMARIES_EBU3213_E', 'PRIMARIES_FILM',
    'PRIMARIES_ST170_M', 'PRIMARIES_ST240_M', 'PRIMARIES_ST428', 'PRIMARIES_ST431_2', 'PRIMARIES_ST432_1',
    'PRIMARIES_UNSPECIFIED', 'RANGE_FULL', 'RANGE_LIMITED', 'RGB', 'SIDE_LEFT', 'SIDE_RIGHT', 'STEREO_LEFT',
    'STEREO_RIGHT', 'SURROUND_DIRECT_LEFT', 'SURROUND_DIRECT_RIGHT', 'TOP_BACK_CENTER', 'TOP_BACK_LEFT',
    'TOP_BACK_RIGHT', 'TOP_CENTER', 'TOP_FRONT_CENTER', 'TOP_FRONT_LEFT', 'TOP_FRONT_RIGHT', 'TRANSFER_ARIB_B67',
    'TRANSFER_BT470_BG', 'TRANSFER_BT470_M', 'TRANSFER_BT601', 'TRANSFER_BT709', 'TRANSFER_BT2020_10',
    'TRANSFER_BT2020_12', 'TRANSFER_IEC_61966_2_1', 'TRANSFER_IEC_61966_2_4', 'TRANSFER_LINEAR', 'TRANSFER_LOG_100',
    'TRANSFER_LOG_316', 'TRANSFER_ST240_M', 'TRANSFER_ST2084', 'TRANSFER_UNSPECIFIED', 'UNDEFINED', 'VIDEO',
    'WIDE_LEFT', 'WIDE_RIGHT', 'YUV', 'AudioChannels', 'AudioFrame', 'AudioNode',
    'CallbackData', 'ChromaLocation', 'ColorFamily', 'ColorPrimaries', 'ColorRange', 'Core', 'CoreCreationFlags',
    'Environment', 'EnvironmentData', 'EnvironmentPolicy', 'EnvironmentPolicyAPI', 'Error', 'FieldBased', 'FilterMode',
    'FrameProps', 'FramePtr', 'Func', 'FuncData', 'Function', 'LogHandle', 'MatrixCoefficients', 'MediaType',
    'MessageType', 'Plugin', 'PresetFormat', 'PythonVSScriptLoggingBridge', 'RawFrame', 'RawNode', 'SampleType',
    'StandaloneEnvironmentPolicy', 'TransferCharacteristics', 'VideoFormat', 'VideoFrame', 'VideoNode',
    'VideoOutputTuple', 'VSScriptEnvironmentPolicy', '__api_version__', '__pyx_capi__', '__version__',
    '_construct_parameter', '_construct_type', '_CoreProxy', 'ccfDisableAutoLoading', 'ccfDisableLibraryUnloading',
    'ccfEnableGraphInspection', 'clear_output', 'clear_outputs', 'construct_signature', 'core', 'fmFrameState',
    'fmParallel', 'fmParallelRequests', 'fmUnordered', 'get_current_environment', 'get_output', 'get_outputs',
    'has_policy', 'register_policy',
    'GRAY8', 'GRAY9', 'GRAY10', 'GRAY11', 'GRAY12', 'GRAY13', 'GRAY14', 'GRAY15', 'GRAY16', 'GRAY17', 'GRAY18',
    'GRAY19', 'GRAY20', 'GRAY21', 'GRAY22', 'GRAY23', 'GRAY24', 'GRAY25', 'GRAY26', 'GRAY27', 'GRAY28', 'GRAY29',
    'GRAY30', 'GRAY31', 'GRAY32', 'GRAYH', 'GRAYS',
    'YUV420P8', 'YUV420P9', 'YUV420P10', 'YUV420P11', 'YUV420P12',
    'YUV420P13', 'YUV420P15', 'YUV420P16', 'YUV420P17', 'YUV420P18', 'YUV420P19', 'YUV420P20', 'YUV420P21', 'YUV420P22',
    'YUV420P23', 'YUV420P24', 'YUV420P25', 'YUV420P26', 'YUV420P27', 'YUV420P28', 'YUV420P29', 'YUV420P30', 'YUV420P31',
    'YUV420P32', 'YUV420PH', 'YUV420PS',
    'YUV444P8', 'YUV444P9', 'YUV444P10', 'YUV444P11', 'YUV444P12', 'YUV444P13',
    'YUV444P14', 'YUV444P15', 'YUV444P16', 'YUV444P17', 'YUV444P18', 'YUV444P19', 'YUV444P20', 'YUV444P21', 'YUV444P22',
    'YUV444P23', 'YUV444P24', 'YUV444P25', 'YUV444P26', 'YUV444P27', 'YUV444P28', 'YUV444P29', 'YUV444P30', 'YUV444P31',
    'YUV444P32', 'YUV444PH', 'YUV444PS',
    'YUV422P8', 'YUV422P9', 'YUV422P10', 'YUV422P11', 'YUV422P12', 'YUV422P13',
    'YUV422P14', 'YUV422P15', 'YUV422P16', 'YUV422P17', 'YUV422P18', 'YUV422P19', 'YUV422P20', 'YUV422P21', 'YUV422P22',
    'YUV422P23', 'YUV422P24', 'YUV422P25', 'YUV422P26', 'YUV422P27', 'YUV422P28', 'YUV422P29', 'YUV422P30', 'YUV422P31',
    'YUV422P32', 'YUV422PH', 'YUV422PS',
    'YUV411P8', 'YUV411P9', 'YUV411P10', 'YUV411P11', 'YUV411P12', 'YUV411P13',
    'YUV411P14', 'YUV411P15', 'YUV411P16', 'YUV411P17', 'YUV411P18', 'YUV411P19', 'YUV411P20', 'YUV411P21', 'YUV411P22',
    'YUV411P23', 'YUV411P24', 'YUV411P25', 'YUV411P26', 'YUV411P27', 'YUV411P28', 'YUV411P29', 'YUV411P30', 'YUV411P31',
    'YUV411P32', 'YUV411PH', 'YUV411PS',
    'YUV440P8', 'YUV440P9', 'YUV440P10', 'YUV440P11', 'YUV440P12', 'YUV440P13',
    'YUV440P14', 'YUV440P15', 'YUV440P16', 'YUV440P17', 'YUV440P18', 'YUV440P19', 'YUV440P20', 'YUV440P21', 'YUV440P22',
    'YUV440P23', 'YUV440P24', 'YUV440P25', 'YUV440P26', 'YUV440P27', 'YUV440P28', 'YUV440P29', 'YUV440P30', 'YUV440P31',
    'YUV440P32', 'YUV440PH', 'YUV440PS',
    'YUV410P8', 'YUV410P9', 'YUV410P10', 'YUV410P11', 'YUV410P12', 'YUV410P13',
    'YUV410P14', 'YUV410P15', 'YUV410P16', 'YUV410P17', 'YUV410P18', 'YUV410P19', 'YUV410P20', 'YUV410P21', 'YUV410P22',
    'YUV410P23', 'YUV410P24', 'YUV410P25', 'YUV410P26', 'YUV410P27', 'YUV410P28', 'YUV410P29', 'YUV410P30', 'YUV410P31',
    'YUV410P32', 'YUV410PH', 'YUV410PS',
    'RGB24', 'RGB27', 'RGB30', 'RGB33', 'RGB36', 'RGB39', 'RGB42', 'RGB45',
    'RGB48', 'RGB51', 'RGB54', 'RGB57', 'RGB60', 'RGB63', 'RGB66', 'RGB69', 'RGB72', 'RGB75', 'RGB78', 'RGB81',
    'RGB84', 'RGB87', 'RGB90', 'RGB93', 'RGB96', 'RGBH', 'RGBS'
]

if not TYPE_CHECKING:
    from vapoursynth import _try_enable_introspection  # noqa F401
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

        return getattr(function, name)  # type: ignore

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

        return getattr(plugin, name)  # type: ignore


class CoreProxy(CoreProxyBase):
    def __init__(self, core: Core) -> None:
        self.__dict__['vs_core_ref'] = weakref.ref(core)

    def __getattr__(self, name: str) -> Plugin:
        core = proxy_utils.get_vs_core(self)

        if name in dir(core):
            return PluginProxy(self, name)

        return getattr(core, name)  # type: ignore


class proxy_utils:
    @staticmethod
    def get_vs_core(core: CoreProxy) -> Core:
        vs_core_ref = core.__dict__['vs_core_ref']

        if (vs_core := vs_core_ref()) is None:
            raise CustomRuntimeError('The VapourSynth core has been freed!', CoreProxy)

        return vs_core  # type: ignore

    @staticmethod
    def get_vs_function(func: FunctionProxy) -> Function:
        plugin, func_name = proxy_utils.get_plugin(func)
        core, namespace = proxy_utils.get_core(plugin)
        vs_core = proxy_utils.get_vs_core(core)

        return getattr(getattr(vs_core, namespace), func_name)  # type: ignore

    @staticmethod
    def get_plugin(func: FunctionProxy) -> tuple[PluginProxy, str]:
        return func.__dict__['func_ref']  # type: ignore

    @staticmethod
    def get_core(plugin: PluginProxy) -> tuple[CoreProxy, str]:
        return plugin.__dict__['plugin_ref']  # type: ignore


builtins_isinstance = builtins.isinstance


def vstools_isinstance(
    __obj: object, __class_or_tuple: type | UnionType | tuple[type | UnionType | tuple[Any, ...], ...]
) -> bool:
    if __class_or_tuple in {_CoreProxy, Core} and builtins_isinstance(__obj, CoreProxy):
        return True

    if __class_or_tuple is VSPresetFormat and builtins_isinstance(__obj, PresetFormat):
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
        return getattr(_get_core(self), name)  # type: ignore

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

if TYPE_CHECKING:
    class PyCapsule(Structure):
        ...

    __pyx_capi__: dict[str, PyCapsule] = ...  # type: ignore

    class StandaloneEnvironmentPolicy(EnvironmentPolicy):
        def __init__(self) -> NoReturn:  # type: ignore[misc]
            ...

        def _on_log_message(self, level: MessageType, msg: str) -> None:
            ...

        def on_policy_registered(self, api: 'EnvironmentPolicyAPI') -> None:
            ...

        def on_policy_cleared(self) -> None:
            ...

        def get_current_environment(self) -> EnvironmentData:
            ...

        def set_environment(self, environment: EnvironmentData | None) -> EnvironmentData:
            ...

        def is_alive(self, environment: EnvironmentData) -> bool:
            ...

    class VSScriptEnvironmentPolicy(EnvironmentPolicy):
        def __init__(self) -> NoReturn:  # type: ignore[misc]
            ...

        def on_policy_registered(self, policy_api: 'EnvironmentPolicyAPI') -> None:
            ...

        def on_policy_cleared(self) -> None:
            ...

        def get_current_environment(self) -> EnvironmentData | None:
            ...

        def set_environment(self, environment: EnvironmentData | None) -> EnvironmentData | None:
            ...

        def is_alive(self, environment: EnvironmentData) -> bool:
            ...

    def _construct_type(signature: str) -> type:
        ...

    def _construct_parameter(signature: str) -> Parameter:
        ...

    class CallbackData:
        def __init__(
            self, node: RawNode, env: EnvironmentData,
            callback: Callable[[RawFrame | None, Exception | None], None] | None = None
        ) -> None:
            ...

        def receive(self, n: int, result: RawFrame | Exception) -> None:
            ...

    class PythonVSScriptLoggingBridge(Handler):

        def __init__(self, parent: Handler, level: int = LogLevelUnset) -> None:
            ...

        def emit(self, record: LogRecord) -> None:
            ...
else:
    from vapoursynth import (
        CallbackData, PythonVSScriptLoggingBridge, StandaloneEnvironmentPolicy, VSScriptEnvironmentPolicy, __pyx_capi__,
        _construct_parameter, _construct_type
    )
