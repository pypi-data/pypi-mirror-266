from setuptools import setup, find_packages
from sciveo.version import __version__

setup(
    name='sciveo',
    version=__version__,
    packages=find_packages(),
    install_requires=[
      'numpy>=0.0.0',
      'requests>=0.0.0',
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    extras_require={
      'mon': [
        'psutil>=0.0.0',
      ]
    },
)
