#!/usr/bin/env python

from distutils.core import setup

setup(name='mbtapredict',
      version='0.0',
      description='Simple MBTA prediction code',
      author='Michael Burton',
      author_email='mjburton11@gmail.com',
      packages=['mbtapredict', 'tests'],
      install_requires=['jsonapi_requests', 'numpy']
     )