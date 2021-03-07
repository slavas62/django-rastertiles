from setuptools import setup, find_packages

setup(
    name='django-rastertiles',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    long_description=open('README.rst').read(),
    install_requires=[
        'python-mapnik',
        'sphericalmercator',
    ],
)
