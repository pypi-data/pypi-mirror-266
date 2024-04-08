"""Dynamic configuration for Setuptools."""

from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            name="uwuifier._uwuifier",
            include_dirs=["src"],
            sources=["src/uwuifier/_uwuifier.c"],
        ),
    ],
)
