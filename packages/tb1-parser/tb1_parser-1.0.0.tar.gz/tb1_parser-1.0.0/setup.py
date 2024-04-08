from setuptools import setup

setup(
      name='tb1_parser',
      version='1.0.0',

      author='ss3n_clam',
      author_email='glebrodionov1993@gmail.com',

      description='ТБ1 парсер',

      url='https://github.com/ss3nclam/tb1_parser',

      packages=['tb1_parser'],
      install_requires=['xlrd', 'pandas', 'transliterate'],

      zip_safe=False
      )