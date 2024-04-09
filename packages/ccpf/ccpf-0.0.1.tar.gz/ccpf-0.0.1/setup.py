from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext


if __name__ == "__main__":
    ext_modules = [
        Extension(
            name="native",
            sources=["native/ccpf/ccpf.c", "native/ccpf_cython.pyx"],
            include_dirs=["native/ccpf"],
            libraries=[],
            library_dirs=[],
            extra_compile_args=[],
            extra_link_args=[],
            language="c99",
        )
    ]
    setup(
        ext_modules=cythonize(ext_modules),
    )
