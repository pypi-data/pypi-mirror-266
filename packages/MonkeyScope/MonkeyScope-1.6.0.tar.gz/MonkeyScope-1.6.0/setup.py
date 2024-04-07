from setuptools import setup, Extension
from Cython.Build import cythonize
from platform import system


with open("README.md", "r") as file:
    long_description = file.read()

compiler_args = {
    "Darwin": ["-std=gnu++20", "-Ofast"],
    "Linux": ["-std=gnu++17", "-O3"],
    "Windows": ["/std:c++20", "/O2"],
}.get(system())

setup(
    name="MonkeyScope",
    url='https://github.com/BrokenShell/MonkeyScope',
    ext_modules=cythonize(
        Extension(
            name="MonkeyScope",
            sources=["MonkeyScope.pyx"],
            language=["c++"],
            extra_compile_args=compiler_args,
        ),
        compiler_directives={
            'embedsignature': True,
            'language_level': 3,
        },
    ),
    author="Robert Sharp",
    author_email="webmaster@sharpdesigndigital.com",
    version="1.6.0",
    description="Distributions & Timer for Non-deterministic Value Generators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Free for non-commercial use",
    platforms=["Darwin", "Linux"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Cython",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "MonkeyScope", "distribution tests", "function timer",
        "performance testing", "statistical analysis",
    ],
    python_requires='>=3.7',
)
