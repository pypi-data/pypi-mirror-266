# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from os import path
import os
import setuptools
import sys
from setuptools import Extension, setup
import site
import platform
from wheel.bdist_wheel import bdist_wheel
from pathlib import Path
from subprocess import run

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None


# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
def no_cythonize(extensions, **_ignore):
    for extension in extensions:
        sources = []
        for sfile in extension.sources:
            filepath, ext = path.splitext(sfile)
            if ext in (".pyx", ".py"):
                if extension.language == "c++":
                    ext = ".cpp"
                else:
                    ext = ".c"
                sfile = filepath + ext
            sources.append(sfile)
        extension.sources[:] = sources
    return extensions


def get_mac_target_architecture():
    if os.environ.get("TARGET_ARCH") == "arm64":
        return "arm64"
    else:
        return "x86_64"


def change_dependency_path_on_mac(build_folder):
    # The lib folder name may be: lib.macosx-13-x86_64-cpython-310
    lib_folders = [path for path in build_folder.iterdir() if path.name.startswith("lib.")]
    if not lib_folders:
        raise RuntimeError("ls lib folder fail when convert rpath to loader_path in .so")
    for lib_folder in lib_folders:
        # The so file name may be: pymsalruntime.cpython-310-darwin.so
        runtime_folder = lib_folder / "pymsalruntime"
        so_files = [path for path in runtime_folder.iterdir() if path.name.startswith("pymsalruntime.cpython")]
        if not so_files:
            raise RuntimeError("ls so file fail when convert rpath to loader_path in .so")
        # internal_arch = "x86_64" if args.arch == "x64" else args.arch
        internal_arch = get_mac_target_architecture()
        for so_file in so_files:
            run(
                [
                    "install_name_tool",
                    "-change",
                    "@rpath/libmsalruntime.dylib",
                    f"@loader_path/libmsalruntime_{internal_arch}.dylib",
                    so_file,
                ],
                check=True,
            )
            run(
                [
                    "install_name_tool",
                    "-change",
                    f"libpyRunloopAPIs_{internal_arch}.dylib",
                    f"@loader_path/libpyRunloopAPIs_{internal_arch}.dylib",
                    so_file,
                ],
                check=True,
            )
    print("Change cython .so depencencies successfullly.")


def get_dependent_library_path_linux():
    site_packages = site.getusersitepackages()
    relative_path = "pymsalruntime"
    library_path = os.path.join(site_packages, relative_path)
    return library_path


class CustomBdistWheelCommand(bdist_wheel):
    def run(self):
        # Custom actions here
        if platform.system() == "Darwin":
            current_path = Path.cwd()
            print("Current Path:", current_path)
            change_dependency_path_on_mac(current_path / f"build")

        super().run()


arch_args = []
extra_ext_args = []

if platform.system() == "Windows":
    library_list = ["msalruntime"] if sys.maxsize > 2**32 else ["msalruntime_x86"]
    library_list.append("user32")
elif platform.system() == "Darwin":
    library_list = [f"msalruntime_{get_mac_target_architecture()}", f"pyRunloopAPIs_{get_mac_target_architecture()}"]
    arch_args += ["-arch", get_mac_target_architecture()]
elif platform.system() == "Linux":
    library_list = ["msalruntime"]
    extra_ext_args += ["-fsanitize=undefined", f"-Wl,-rpath,{get_dependent_library_path_linux()}"]
else:
    library_list = []

ext_modules = [
    Extension(
        name="pymsalruntime.pymsalruntime",
        sources=["pymsalruntime/PyMsalRuntime.pyx"],
        libraries=library_list,
        library_dirs=["build_resources"],  # At build time the most recently built version of
        # the .h, .lib, is copied here for compilation.
        include_dirs=["build_resources"],
        # Uncomment below for producing PDB to debug.
        # extra_compile_args=["-Ox", "-Zi"],
        # extra_link_args=["-debug:full"],
        # extra_compile_args=["-O0"],
        extra_compile_args=arch_args,
        extra_link_args=arch_args,
    )
]

if cythonize:  # Cythonize pyx files to .c files if we can, or assume precompiled sources are included.
    compiler_directives = {"language_level": 3, "embedsignature": True}
    ext_modules = cythonize(ext_modules, compiler_directives=compiler_directives)
else:
    ext_modules = no_cythonize(ext_modules)

version_file_path = path.normpath(path.join(path.dirname(__file__), "version.txt"))
with open(version_file_path, "r") as version_file:
    runtime_version = version_file.read().strip()

if platform.system() == "Linux":
    ext_modules[0].extra_compile_args += extra_ext_args
    ext_modules[0].extra_link_args += extra_ext_args

setup(
    name="pymsalruntime",
    version=runtime_version,
    description="The MSALRuntime Python Interop Package",
    author="Microsoft Corporation",
    license="MIT",
    author_email="MSALRuntime@microsoft.com",
    python_requires=">=3.6",
    packages=["pymsalruntime"],  # At build time the most recently built version of
    # the .dll copied here for distribution.
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    package_data={
        "": ["*.so", "*.dylib", "*.dll", "*.pyi"],
    },
    ext_modules=ext_modules,
    cmdclass={
        "bdist_wheel": CustomBdistWheelCommand,  # Use your custom class
    },
)
