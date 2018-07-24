from setuptools import setup, find_packages

setup(
    name='agavecli',
    version='0.1.0',
    author='alejandrox1',
    packages=find_packages(),
    install_requires=[
        'future',  
        'requests',
      ],
    entry_points={'console_scripts': ['agavecli = agavecli.__main__:main']})
