load("@rules_uv//uv:pip.bzl", "pip_compile")
load("@rules_uv//uv:venv.bzl", "create_venv")

pip_compile(
    name = "generate_requirements_txt",
    requirements_in = "//:requirements.in",
    requirements_txt = "//:requirements.txt",
)

create_venv(
    name = "create_venv",
    requirements_txt = "//:requirements.txt",
)
