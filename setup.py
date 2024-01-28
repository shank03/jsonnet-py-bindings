import os

from setuptools.command.build_clib import build_clib
from setuptools import Extension, setup

r = os.system("cd jsonnet && git reset --hard && git apply ../windows.patch && cd ..")
if r != 0:
    print("Error applying windows patch to google/jsonnet")
    exit()

LIB_INCLUDES: list[str] = [
    "jsonnet/include",
    "jsonnet/third_party/json",
    "jsonnet/third_party/md5",
    "jsonnet/third_party/rapidyaml/rapidyaml/src",
    "jsonnet/third_party/rapidyaml/rapidyaml/src/c4",
    "jsonnet/third_party/rapidyaml/rapidyaml/src/c4/std",
    "jsonnet/third_party/rapidyaml/rapidyaml/src/c4/detail",
    "jsonnet/third_party/rapidyaml/rapidyaml/ext/c4core/src",
]

LIB_SOURCES: list[str] = [
    "jsonnet/core/desugarer.cpp",
    "jsonnet/core/formatter.cpp",
    "jsonnet/core/libjsonnet.cpp",
    "jsonnet/core/lexer.cpp",
    "jsonnet/core/parser.cpp",
    "jsonnet/core/pass.cpp",
    "jsonnet/core/static_analysis.cpp",
    "jsonnet/core/string_utils.cpp",
    "jsonnet/core/vm.cpp",
    "jsonnet/third_party/md5/md5.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/ext/c4core/src/c4/char_traits.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/ext/c4core/src/c4/base64.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/ext/c4core/src/c4/language.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/ext/c4core/src/c4/memory_util.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/ext/c4core/src/c4/format.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/ext/c4core/src/c4/time.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/ext/c4core/src/c4/memory_resource.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/ext/c4core/src/c4/error.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/src/c4/yml/parse.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/src/c4/yml/preprocess.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/src/c4/yml/common.cpp",
    "jsonnet/third_party/rapidyaml/rapidyaml/src/c4/yml/tree.cpp",
]


class BuildCLib(build_clib):
    """Builds jsonnet library"""

    cflags = {
        "msvc": ["/EHsc", "/Ox", "/std:c++17"],
        "unix": [
            "-g",
            "-O3",
            "-Wall",
            "-Wextra",
            "-Woverloaded-virtual",
            "-pedantic",
            "-std=c++17",
            "-fPIC",
        ],
    }

    def _buildstdlib(self):
        """Builds the byte-array for stdlib."""

        with open("jsonnet/stdlib/std.jsonnet", "rb") as f:
            stdlib = bytearray(f.read())
        with open("jsonnet/core/std.jsonnet.h", "w") as f:
            for byte in stdlib:
                f.write("%d," % byte)
            f.write("0")

    def _patchcflags(self, libraries):
        """Add in cflags."""

        compiler = self.compiler.compiler_type
        args = self.cflags[compiler]
        for lib in libraries:
            lib[1]["cflags"] = args

    def build_libraries(self, libraries):
        self._patchcflags(libraries)
        self._buildstdlib()
        super(BuildCLib, self).build_libraries(libraries)


DIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(DIR, "README.md"), encoding="utf-8") as f:
    readme = f.read()


def get_version():
    """
    Parses the version out of libjsonnet.h
    """
    with open(os.path.join(DIR, "jsonnet/include/libjsonnet.h")) as f:
        for line in f:
            if "#define" in line and "LIB_JSONNET_VERSION" in line:
                v_code = line.partition("LIB_JSONNET_VERSION")[2].strip('\n "')
                if v_code[0] == "v":
                    v_code = v_code[1:]
                return v_code

    return "0.20.0"


post_release_segment = ""  # ".post0"
"""
The post release segment of jsonnet-bindings, appended after version of jsonnet.

It should be defined to release a new version of jsonnet-bindings packages, but jsonnet version is still the same.

`See PEP 440 Post Releases <https://www.python.org/dev/peps/pep-0440/#post-releases>`_.
"""

setup(
    name="jsonnet-bindings",
    url="https://github.com/shank03/jsonnet-py-bindings",
    description="An UNOFFICIAL Python bindings for Jsonnet, "
    "available as whl packages for Mac, Linux and Windows.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Matt Covalt",
    author_email="mcovalt@mailbox.org",
    maintainer="Shashank Verma",
    maintainer_email="shashank.verma2002@gmail.com",
    version=get_version() + post_release_segment,
    ext_modules=[
        Extension(
            "_jsonnet",
            sources=["jsonnet/python/_jsonnet.c"],
            libraries=["jsonnet"],
            include_dirs=[
                "jsonnet/include",
                "jsonnet/third_party/json",
                "jsonnet/third_party/md5",
            ],
            language="c++",
        )
    ],
    libraries=[
        [
            "jsonnet",
            {
                "sources": LIB_SOURCES,
            },
        ],
    ],
    include_dirs=LIB_INCLUDES,
    cmdclass={"build_clib": BuildCLib},
)

print("SETUP DONE")
