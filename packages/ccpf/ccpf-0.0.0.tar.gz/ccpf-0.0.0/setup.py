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

# with open("README.md", "r", encoding="utf-8") as f:
#     long_description = f.read()

#
# setup(
#     name="ccpf",
#     version="0.0.1",
#     author="asimos-bot",
#     author_email="felipe.asimos@gmail.com",
#     license="MIT",
#
#     description="CPF validation, generation and masking",
#     long_description=long_description,
#     packages=find_packages(),
#     keywords=["cpf", "validation", "generation", "mask"],
#     classifiers=[
#         "Development Status :: 1 - Planning",
#         "Intended Audience :: Developers",
#         "Programming Language :: Python :: 3",
#         "Programming Language :: C",
#         "Operating System :: OS Independent",
#         "License :: OSI Approved :: MIT License",
#         "Topic :: Software Development :: Libraries :: Python Modules"
#     ],
#     url="https://github.com/asimos-bot/ccpf",
#     test_suite="tests",
#     tests_require=["tox"],
#     zip_safe=True,
#     ext_modules=cythonize(ext_modules),
# )
