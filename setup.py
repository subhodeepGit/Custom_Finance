from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in custom_finance/__init__.py
from custom_finance import __version__ as version

setup(
	name="custom_finance",
	version=version,
	description="SOUL",
	author="SOUL",
	author_email="soul@soulunileaders.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
