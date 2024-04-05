# -*- coding: utf-8 -*-
import os
from io import open
from setuptools import setup
from setuptools import find_packages
from django_model_helper import version

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires = fobj.readlines()
requires = [x.strip() for x in requires if x.strip()]


setup(
    name="django-model-helper",
    version=version.VERSION,
    description="Helpful django abstract models collection.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Li HuiTao",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["django-model-helper"],
    install_requires=requires,
    packages=find_packages(
        ".",
        exclude=[
            "django_model_helper_demo",
            "django_model_helper_example",
            "django_model_helper_example.migrations",
        ],
    ),
    zip_safe=False,
    include_package_data=True,
)
