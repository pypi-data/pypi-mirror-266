# -*- coding: utf-8 -*-
# # Copyright by sn0wfree 2018
# ----------------------------
from setuptools import setup, find_packages

import CodersWheel

__Version__ = CodersWheel.__Version__
__Author__ = CodersWheel.__Author__
# __Description__ = CodersWheel.__Description__


setup(name='CodersWheel',
      version=__Version__,
      url='https://github.com/sn0wfree',
      license='MIT',
      author=" & ".join(__Author__),
      author_email="snowfreedom0815@gmail.com",
      include_packages_data=True,
      description='CodersWheel - CW',
      packages=find_packages(exclude=[]),
      long_description=open('README.md', encoding='utf-8').read(),
      zip_safe=False,
      setup_requires=['pandas>=0.24.2'],

      )

if __name__ == '__main__':
    pass
