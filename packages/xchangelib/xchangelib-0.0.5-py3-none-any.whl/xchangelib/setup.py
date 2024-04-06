from setuptools import setup

setup(name='xchangelib',
      version='0.0.5',
      description="Client for xchangeV3",
      long_description="",
      author='Rohan Voddhi',
      author_email='rohan.voddhi@gmail.com',
      license='TODO',
      packages=['xchangelib'],
      zip_safe=False,
      install_requires=[
            'protobuf==5.26.0',
            'grpcio==1.62.1',
      ]
      )