#!/usr/bin/env python
import os
import sys

if sys.version_info < (3, 8):
    print("Error: dbt does not support this version of Python.")
    print("Please upgrade to Python 3.8 or higher.")
    sys.exit(1)


from setuptools import setup

try:
    from setuptools import find_namespace_packages
except ImportError:
    # the user has a downlevel version of setuptools.
    print("Error: dbt requires setuptools v40.1.0 or higher.")
    print('Please upgrade setuptools with "pip install --upgrade setuptools" ' "and try again")
    sys.exit(1)


this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md")) as f:
    long_description = f.read()


package_name = "idbt"
package_version = os.environ["PACKAGE_VERSION"]
description = """This is inter-k internal tool to help data practice becomes more testable"""


setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bảo Phan",
    author_email="bao.phan1441@gmail.com",
    url="https://gitlab.inter-k.com/inter-k/internal-software/rnd/idbt",
    packages=find_namespace_packages(include=["idbt", "idbt.*"]),
    include_package_data=True,
    test_suite="test",
    entry_points={
        "console_scripts": ["idbt = idbt.main:cli"],
    },
    install_requires=[
        # ----
        # dbt-core uses these packages deeply, throughout the codebase, and there have been breaking changes in past patch releases (even though these are major-version-one).
        # Pin to the patch or minor version, and bump in each new minor version of dbt-core.
        "dbt-core>=1.7.0",
    ],
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
)
