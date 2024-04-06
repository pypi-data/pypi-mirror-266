#!/usr/bin/env python
import os
from pathlib import Path
from setuptools import setup, find_packages

BASE_DIR = Path(__file__).resolve().parent
setup(name='ubnesieh',
      version='0.0.1',
      description='',
      long_description=open(os.path.join(BASE_DIR, 'README.md'), 'r').read(),
      long_description_content_type="text/markdown",
      author='ubnesieh',
      author_email='',
      url='',
      packages=find_packages(include=['ubnesieh*', ]),
      package_data={'': ['*.txt'], },
      include_package_data=True,
      install_requires=[
          'torch',
          'pypinyin',
          'tqdm',
          'pyarrow',
          'numpy',
          'pandas',

      ],
      license='LICENSE',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Operating System :: OS Independent',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3 :: Only",
          'Topic :: Software Development :: Libraries'
      ],
      )
