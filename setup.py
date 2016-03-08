from setuptools import setup

with open('README.md') as rfile:
    long_description = rfile.read()

setup(name='prespy',
      version='0.0.3',
      description='Package for working with the Neurobehavioural Systems' +
                  ' Presentation logfiles within python',
      long_description=long_description,
      url='https://github.com/gjcooper/prespy',
      author='Gavin Cooper',
      author_email='gjcooper@gmail.com',
      license='GPL v2.0',
      packages=['prespy'],
      keywords=['Presentation', 'NBS', 'logfile'])
