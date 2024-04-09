
LONG_DESCRIPTION = """\
This is intended as a tool box to enable easy coding in Python of agorithms
that operate with logical representations."""  

from setuptools import setup
setup(
    name='bs_logic',
    version='0.0.8',
    description='Utilities for implementing logical representaions and reasoning systems',
    long_description = (
     "This is intended as a tool box to enable easy coding in Python of agorithms "
     "that operate with logical representations."   
    ),
    #url = 'https://bb-ai.net/KARaML/KARaML_Tools.html',
    author = 'Brandon Bennett and Giulia Sindoni',
    author_email='B.Bennett@leeds.ac.uk',
    packages=['bs_logic'],
    include_package_data = True,
    classifiers=['Development Status :: 1 - Planning'],
)
