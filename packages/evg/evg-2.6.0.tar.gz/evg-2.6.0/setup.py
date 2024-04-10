from setuptools import setup, find_packages

with open("../README.md", "r") as fh:
    long_description = fh.read()

setup(name='evg',
      version='2.6.0',
      url='https://github.com/IceOne-i/evg',
      license='MIT',
      author='Nikita Belan',
      author_email='nikitabelan9@gmail.com',
      description='Discord translator & translation of Discord functions/interactions',
      long_description=long_description,
      long_description_content_type="text/markdown",
      zip_safe=False)
