load("@aspect_rules_py//py:defs.bzl", "py_library")

py_library(
    name = "actuator",
    srcs = ["actuator.py"],
    deps = [
        ":manage_high_speed_stream",
        ":motor_command_stream",
        ":motor_read_stream",
        ":motor_write_stream",
    ],
    visibility = ["//visibility:public"],
)

py_library(
    name = "bit_utils",
    srcs = ["bit_utils.py.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "constants",
    srcs = ["constants.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "manage_high_speed_stream",
    srcs = ["manage_high_speed_stream.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "motor_command_stream",
    srcs = ["motor_command_stream.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "motor_read_stream",
    srcs = ["motor_read_stream.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "motor_write_stream",
    srcs = ["motor_write_stream.py"],
    visibility = ["//visibility:public"],
)
