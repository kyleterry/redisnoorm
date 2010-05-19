from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='redisnoorm',
      version=version,
      description="redis orm",
      long_description="""\
redis orm thing""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='redis orm model',
      author='Kyle Terry',
      author_email='kyle@kyleterry.com',
      url='http://kyleterry.com',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
