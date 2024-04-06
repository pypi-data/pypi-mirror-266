from setuptools import find_packages, setup

setup(
    name='pyscinloopsr',
    packages=find_packages(include=['pyscinloopsr']),
    version='1.0.1',
    description='Facilitator for scientists in the loop of SR modelling',
    author='Djalma Pereira',
    #install_requires='pysr'
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'], #tests_require=['pytest==4.4.1'],
    test_suite='tests',
)