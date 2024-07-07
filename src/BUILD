load("@aspect_rules_py//py:defs.bzl", "py_binary")

py_binary(
    name = "main",
    srcs = ["main.py"],
    deps = [
        "@pypi//pymodbus",
        "@pypi//pynput",
        "//src/bytemachine:lib_bytemachine",
        "//src/orca:actuator",
        "//src/orca:constants",
        "//src/orca:manage_high_speed_stream",
        "//src/orca:motor_command_stream",
        "//src/orca:motor_read_stream",
        "//src/orca:motor_write_stream",
    ],
)
