import sys,os
from setuptools import setup, find_packages, Command

class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call([sys.executable, '-m', 'pytest'])
        raise SystemExit(errno)

try:
     with open("README.md","r") as f:
          long_description=f.read()
except:
     long_description=""
     pass

setup(name='amolkit', 
      version='1.0.4', 
      description='Library for extracting molecule information', 
      long_description=long_description,
      url='https://github.com/anmolecule/amolkit', 
      author='Anmol Kumar', 
      author_email='anmolecule@gmail.com', 
      license='BSD 3-Clause "New" or "Revised" License',
      packages=find_packages(), 
      cmdclass={'test': PyTest},  
      zip_safe=False)

