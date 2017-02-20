from setuptools import setup, find_packages
from os import path

__version__ = '0.0.4'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' not in x]

setup(
    name='prespy',
    version=__version__,
    description='Package for working with the Neurobehavioural Systems' +
                ' Presentation logfiles within python',
    long_description=long_description,
    url='https://github.com/gjcooper/prespy',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    author='Gavin Cooper',
    author_email='gjcooper@gmail.com',
    install_requires=install_requires,
    dependency_links=dependency_links,
    license='GPL v2.0',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    keywords=['Presentation', 'NBS', 'logfile'],
    entry_points={
        'console_scripts': ['scla=prespy.__main__:scla'],
    }
)
