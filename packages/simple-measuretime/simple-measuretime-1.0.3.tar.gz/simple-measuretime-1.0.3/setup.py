from setuptools import setup, find_packages

setup(
  name='simple-measuretime',
  version='1.0.3',
  author='seyuriti',
  author_email='aesioseyuri@gmail.com',
  description='This is a simple package to measure the time in Python.',
  packages=find_packages(),
  classifiers=[
  'Programming Language :: Python :: 3',
  'License :: OSI Approved :: MIT License',
  'Operating System :: OS Independent',
  ],
  python_requires='>=3.6',
)