#!/usr/bin/env python
# encoding: utf-8


from setuptools import setup, find_packages
from bibmatch import __package__, __description__, __version__


setup(name=__package__,
      version=__version__,
      description='bibliographic matching',
      long_description=__description__,
      classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6',
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering :: Information Analysis',
      ],
      keywords="database",
      url="https://github.com/kasoju2712/Bibliometric-Matching",
      author = 'Apoorva Kasoju <apoorva.kasoju2712@gmail.com> \n Alex Gates <ajgates42@gmail.com> \n Qing Ke <keqing.echolife@gmail.com>',
      license="MIT",
      packages = find_packages(),
      install_requires=[
            'numpy',
            'pandas',
            'nameparser',
            'bs4',
            'langdetect'
      ],
      include_package_data=True
      )
