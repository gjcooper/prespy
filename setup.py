from setuptools import setup

with open('README.md') as rfile:
    long_description = rfile.read()

setup(name='pypres',
      version='0.0.1',
      description='Package for working with the Neurobehavioural Systems' +
                  ' Presentation logfiles within python',
      long_description=long_description,
      url='https://github.com/gjcooper/eegevt',
      author='Gavin Cooper',
      author_email='gjcooper@gmail.com',
      license='GPL v2.0',
      packages=['pypres'],
      keywords=['Presentation', 'NBS', 'logfile'])
