from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(name='generate_random_string',  # 包名
      version='1.0.1',  # 版本号
      description='A package generates a specify length random string,belongs:alphabet、nums or their mix',
      long_description=long_description,
      author='wuguipeng',
      author_email='734426750@qq.com',
      url='',
      install_requires=[],
      license='MIT License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries'
      ],
      )