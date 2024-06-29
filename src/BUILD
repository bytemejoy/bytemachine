load("@rules_python//python:defs.bzl", "py_binary")
load("@rules_python//python:defs.bzl", "py_library")

py_binary(
    name = "controller_main",
    srcs = ["controller_main.py"],
    deps = [
	"@bytemachine_deps//pymodbus",
	"@bytemachine_deps//pyserial",
    ],
)
