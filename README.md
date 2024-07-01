# bytemachine
Source code for the bytemachine from bytemejoy

## Development instructions (how to contribute)

### Build System

This project uses the [bazel build system](https://bazel.build/).

To install/use bazel, I **highly** recommend using [bazelisk](https://github.com/bazelbuild/bazelisk) which greatly
simplifies bazel setup, will keep your bazel version up to date, and has
excellent cross-platform support.

Both `requirements.txt` generation and `venv` generation are handled by
[rules_uv](https://github.com/theoremlp/rules_uv).

Aspect Build's `rules_py` is used for the `py_*` rules which has a few very 
nice benefits:
* No system interpreter dependency
* `$PYTHONPATH` and `sys.path` are never touched
* Python is run in isolated mode which prevents escaping Bazel's sandbox
* First-class `virtualenv` support

### Development Setup

The following assumes that you have aliased the `bazelisk` command to `bazel`.

To update `requirements.txt`:
* `bazel run @@//:generate_requirements_txt`

To generate the development `venv` for use in an IDE (whichever one your heart
desires):
* `bazel run @@//:create_venv`

### Project Overview

The main entrypoint for this project is `//src:main` which starts up the motor
controller.

Motor mode, movement, speed, etc. is controlled either via the command line or
using the rotary encoders which have pre-defined function mappings.

Communication with the `orca` motor uses `modbus` which leans almost entirely
on `pymodbus`.


## Hardware Bill of Materials (so far)

### Motor
* [ORCA-6-LITE](https://irisdynamics.com/products/orca-series)

### Power/Wiring
* [Meanwell MSP-1000-24](https://www.digikey.ca/en/products/detail/mean-well-usa-inc/MSP-1000-24/9602709)
* [Wago 221 Series Lever-Nuts](https://www.wago.com/us/lp-221)
* [Qizpcer 10 AWG Inline Fuse Holder](https://www.amazon.com/dp/B08K3NLV27?ref=ppx_yo2ov_dt_b_product_details&th=1)
* [Chanzon 30A Fast Blow Fuse](https://www.amazon.com/dp/B083QHLRDH)

### Controller
* [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/)
* [Adafruit I2C Quad Rotary Encoder](https://www.adafruit.com/product/5752)
* [Adafruit Rotary Encoder + Extras x4](https://www.adafruit.com/product/377)
* [Adafruit Clear Micro Potentiometer Knob x4](https://www.adafruit.com/product/5676)
* [SparkFun Qwiic or Stemma QT SHIM for Raspberry Pi](https://www.adafruit.com/product/4463)
