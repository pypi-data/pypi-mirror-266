#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import io
from setuptools import setup, find_packages


setup(name='rebookmaker',
      version='0.8.11',
      description='EPUB generator',
      keywords='rebookmaker',
      author='Shlomi Fish',
      author_email='shlomif@cpan.org',
      url='https://github.com/shlomif/rebookmaker',
      license='3-clause BSD',
      long_description=io.open(
          './docs/README.rst', 'r', encoding='utf-8').read(),
      platforms='any',
      zip_safe=False,
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 1 - Planning',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3.9',
                   'Programming Language :: Python :: 3.10',
                   'Programming Language :: Python :: 3.11',
                   ],
      packages=find_packages(exclude=('tests', 'tests.*')),
      include_package_data=True,
    package_data={'': ['data/templates/*.jinja','data/templates/*.png','data/templates/*.xcf'],},
    scripts=['rebookmaker/rebookmaker'],
      install_requires=['beautifulsoup4','coverage','importlib_resources>=6.0','jinja2>=3.0.1','lxml','markupsafe','pytest','pytest-cov','requests','twine'],
      
      )
