# Changelog

This is a list of all the noteworthy changes made to vs-tools.

For a complete list of release tags and their corresponding changes,
see the [tags page](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/tags).

---

## Latest

- FunctionUtil:
  - Resolved an issue where it would raise a vs.Error when resampling RGB to YUV or GRAY without a matrix specified instead of an UndefinedMatrixError.
  - Make use of early exits in `norm_clip` to reduce unnecessary processing
  - Improved class functionality ([#152](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/pull/152)):
    - Removed `strict` parameter
    - Added support for transfer, primaries, chroma location, and field order parameters
    - Improved type annotations and docstrings

- vstools.utils.scale module:
  - Improved scaling defaults and behavior ([#145](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/pull/145)):
    - Updated default color range handling for RGB and non-RGB formats
    - Removed unnecessary `@overload` declarations for `scale_value` function
    - Enforced integer output for integer sample types
    - Updated unit tests for integer and float scaling operations

- ChromaLocation:
  - Fixed an issue where `get_offsets` would throw an error on 4:4:4 subsampling (thanks [@shssoichiro](https://github.com/shssoichiro)!)

- Timecodes:
  - Replaced ambiguous variable name

- Removed deprecated functions and parameters ([f75b250](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/commit/f75b250def4b34e69cafb86d0ba3364fe2939607)):
  - Removed `scale_8bit` function
  - Removed `chroma` parameter from `get_neutral_value` function

- Testing and linting:
  - Added tests for `FunctionUtil`
  - Added preliminary test suite ([#149](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/pull/149))
  - Removed smoke test in favor of unit tests ([#153](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/pull/153))
  - Updated lint action to use ruff
  - Added top-level noqa to `__init__.py`

- Other:
  - Improve type-checking for pyright
  - New `is_gpu_available` function to check if any GPU is available

## v3.3.3

**Full Changelog**: https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/compare/v3.3.1...v3.3.3

Hotfix release to resolve some issues involving FunctionUtil in relation to other packages.

- FunctionUtil:
  - Resolved an issue where it would fail when processing clips with bitdepths exceeding the maximum allowed value
  - Extend `range` to be (start, stop + 1) to work around us no longer using `range.stop`
  - Fix a check in `chroma_planes` which would return in it returning an empty list when it should not

## v3.3.1

...
