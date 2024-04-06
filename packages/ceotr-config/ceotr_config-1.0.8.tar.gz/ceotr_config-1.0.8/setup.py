import os
from setuptools import setup, find_packages

path_to_my_project = os.path.dirname(__file__)  # Do any sort of fancy resolving of the path here if you need to


install_requires = [
    "PyYAML",
      "python-dotenv"
]
packages = find_packages(exclude=['tests'])

setup(name='ceotr_config',
      version='1.0.8',
      description="Common python library for CEOTR data team",
      author="CEOTR",
      author_email="support@ceotr.ca",
      url="https://gitlab.oceantrack.org/ceotr-public/ceotr_app_common/ceotr_config",
      packages=packages,
      include_package_data=True,
      license="GNU General Public License v3 (GPLv3)",
      install_requires=install_requires,
      zip_safe=True
      )
