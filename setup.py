from setuptools import setup, find_packages

install_deps = ['sphericalmercator']
if get_dist('mapnik'):
    install_deps.append('mapnik')
else:
    install_deps.append('python3-mapnik')

setup(
    name='django-rastertiles',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    long_description=open('README.rst').read(),
    
    install_requires = install_deps,
)
