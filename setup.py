import os
import shlex
import subprocess  # nosec

from distutils.core import setup, Extension

TOXAV_TEST_CODE = b"""
extern int toxav_new();
int (*x)() = &toxav_new;
int main(){}
"""

def supports_av(libs):
    ldflags = shlex.split(os.environ.get("LDFLAGS", ""))
    proc = subprocess.Popen(  # nosec
        ["cc", "-xc", "-"] + ldflags + libs,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Wait for process to terminate; ignore stdout/stderr.
    proc.communicate(TOXAV_TEST_CODE)

    if os.path.exists("a.out"):
        os.remove("a.out")
        return True
    return False

sources = ["pytox/pytox.c", "pytox/core.c", "pytox/util.c"]
libraries = [
  "opus",
  "sodium",
  "toxcore",
  "vpx",
]
cflags = [
  "-Wall",
  # "-Werror",
  "-Wextra",
  "-Wno-declaration-after-statement",
  "-Wno-missing-field-initializers",
  "-Wno-unused-parameter",
  "-fno-strict-aliasing",
]

if supports_av(["-ltoxcore"]):
    sources.append("pytox/av.c")
    cflags.append("-DENABLE_AV")
elif supports_av(["-ltoxcore", "-ltoxav"]):
    sources.append("pytox/av.c")
    cflags.append("-DENABLE_AV")
    libraries.append("toxav")
else:
    print("Warning: AV support not found, disabled.")

setup(
    name="py-toxcore-c",
    version="0.2.0",
    description="Python binding for Tox the skype replacement",
    author="Wei-Ning Huang (AZ)",
    author_email="aitjcize@gmail.com",
    url="http://github.com/TokTok/py-toxcore-c",
    license="GPL",
    ext_modules=[
        Extension(
            "pytox",
            sources,
            extra_compile_args=cflags,
            libraries=libraries
        )
    ]
)
