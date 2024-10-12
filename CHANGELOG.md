# Changelog

This is a list of all the noteworthy changes made to vs-tools.

For a complete list of release tags and their corresponding changes,
see the [tags page](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/tags).

---

## Latest


- Improved `FunctionUtil` class functionality ([#152](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/pull/152)):
  - Removed `strict` parameter
  - Added support for transfer, primaries, chroma location, and field order parameters
  - Improved type annotations and docstrings

- Improved scaling defaults and behavior in `vstools.utils.scale` module ([#145](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/pull/145)):
  - Updated default color range handling for RGB and non-RGB formats
  - Removed unnecessary `@overload` declarations for `scale_value` function
  - Enforced integer output for integer sample types
  - Updated unit tests for integer and float scaling operations

- Added preliminary test suite ([#149](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/pull/149)):
  - Fixed an issue where `ChromaLocation.get_offsets` would throw an error on 4:4:4 subsampling (thanks [@shssoichiro](https://github.com/shssoichiro)!)

- Removed smoke test in favor of unit tests ([#153](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/pull/153))

- Improved code linting:
  - Replaced ambiguous variable name in Timecodes
  - Updated lint action to use ruff
  - Added top-level noqa to `__init__.py`

- Removed deprecated function and parameters ([f75b250](https://github.com/Jaded-Encoding-Thaumaturgy/vs-tools/commit/f75b250def4b34e69cafb86d0ba3364fe2939607)):
  - Removed `scale_8bit` function
  - Removed `chroma` parameter from `get_neutral_value` function

## v3.3.1

...
