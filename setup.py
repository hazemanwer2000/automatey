
from setuptools import setup, find_packages

setup(name='automatey',
      version='1.0.0',
      description='A collection of Python utilities, and CMD tools.',
      url='https://github.com/hazemanwer2000/automatey',
      author='Hazem Anwer',
      author_email='hazemanwer2000@proton.me',
      license='None',
      install_requires=[
            'click'
      ],
      entry_points={
            'console_scripts' : [
                  'automatey=automatey.cli:GroupCMD_cli'
            ]
      },
      zip_safe=False
)