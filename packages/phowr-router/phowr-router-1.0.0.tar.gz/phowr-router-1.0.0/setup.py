# Copyright 2023 Hao Hoang (haohoangofficial@gmail.com)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import subprocess

try:
    import fastapi
except ImportError:
    try:
        command = ["pip", "install", "fastapi"]
        subprocess.run(command, check=True)
    except Exception:
        command = ["pip3", "install", "fastapi"]
        subprocess.run(command, check=True)
import os

this_dir = os.path.dirname(__file__)
readme_filename = os.path.join(this_dir, 'README.md')
requirements_filename = os.path.join(this_dir, 'requirements.txt')

PACKAGE_NAME = 'phowr-router'
PACKAGE_VERSION = '1.0.0'
PACKAGE_AUTHOR = 'Hao Hoang'
PACKAGE_AUTHOR_EMAIL = 'haohoangofficial@gmail.com'
PACKAGE_URL = 'https://github.com/hdsme/phowr-router'
PACKAGE_DOWNLOAD_URL = \
    'https://github.com/hdsme/phowr-router/tarball/' + PACKAGE_VERSION
PACKAGES = [
    'phowr_router',
]
PACKAGE_DATA = {}
PACKAGE_LICENSE = 'LICENSE.txt'
PACKAGE_DESCRIPTION = 'Phowr Router'

with open(readme_filename) as f:
    PACKAGE_LONG_DESCRIPTION = f.read()

with open(requirements_filename) as f:
    PACKAGE_INSTALL_REQUIRES = [line[:-1] for line in f]

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author=PACKAGE_AUTHOR,
    author_email=PACKAGE_AUTHOR_EMAIL,
    url=PACKAGE_URL,
    download_url=PACKAGE_DOWNLOAD_URL,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    license=PACKAGE_LICENSE,
    description=PACKAGE_DESCRIPTION,
    long_description=PACKAGE_LONG_DESCRIPTION,
    install_requires=PACKAGE_INSTALL_REQUIRES,
    long_description_content_type="text/markdown",
)