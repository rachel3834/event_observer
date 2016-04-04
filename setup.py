#!/usr/bin/env python
import sys
import os

if "publish" in sys.argv[-1]:
    os.system("python setup.py sdist upload")
    sys.exit()

try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup
    setup

# Load the __version__ variable without importing the package
exec(open('scripts/version.py').read())

# Command-line tools; we're not using "entry_points" for now due to
# a bug in pip which turns all the tools into lowercase
scripts = ['scripts/event_observer']

setup(name='event_observer',
      version=__version__,
      description='Submit observation sequences to LCOGT Network',
      author='Rachel Street',
      author_email='rstreet@lcogt.net',
      url='https://github.com/rachel3834/event_observer',
      packages=['event_observer'],
      package_data={'event_observer': []},
      install_requires=[],
      scripts=scripts,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: GNU Public License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7"
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering :: Astronomy",
          ],
      )
