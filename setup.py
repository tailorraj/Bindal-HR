from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in bindal_hr_customization/__init__.py
from bindal_hr_customization import __version__ as version

setup(
	name="bindal_hr_customization",
	version=version,
	description="HR Customization",
	author="Raaj tailor",
	author_email="raaj@akhilaminc.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
