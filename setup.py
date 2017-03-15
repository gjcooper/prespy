from setuptools import setup, find_packages
import codecs
import os
import subprocess
import sys

__version__ = '0.0.6'

base_dir = os.path.abspath(os.path.dirname(__file__))


def genRST():
    pandoc_call = ['pandoc', '--from=markdown', '--to=rst', 'README.md']
    try:
        output = subprocess.run(pandoc_call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output.returncode:
            print(output.stderr)
            sys.exit()
        output = output.stdout
    except AttributeError:
        try:
            output = subprocess.check_output(pandoc_call)
        except subprocess.CalledProcessError:
            sys.exit()
    return output.decode()


# get the dependencies and installs
with codecs.open(os.path.join(base_dir, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' not in x]

setup(
    name='prespy',
    version=__version__,
    description='Package for working with the Neurobehavioural Systems' +
                ' Presentation logfiles within python',
    long_description=genRST(),
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
        'console_scripts': ['pres-scla=prespy.__main__:scla'],
    }
)
