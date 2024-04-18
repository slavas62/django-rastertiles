from setuptools import setup, find_packages
import sys

install_deps = ['sphericalmercator']

if sys.version_info[0] == 3:               # Python version
#    install_deps.append('python3-mapnik')
    pass
else:
    install_deps.append('mapnik')

setup(
    name='django-rastertiles',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    long_description=open('README.rst').read(),
    
    install_requires = install_deps,
)
