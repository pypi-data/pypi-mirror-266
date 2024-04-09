
LONG_DESCRIPTION = """\
This is intended as a tool box to enable easy coding in Python of agorithms
that operate with logical representations."""  



from setuptools import setup
setup(
    name='bs_logic',
    version='0.0.2',
    description='Utilities for implementing logical representaions and reasoning systems',
    long_description = LONG_DESCRIPTION,
    #url = 'https://bb-ai.net/KARaML/KARaML_Tools.html',
    author = 'Brandon Bennett and Giulia Sindoni',
    author_email='B.Bennett@leeds.ac.uk',
    packages=['bs_logic'],
    classifiers=['Development Status :: 1 - Planning'],
)
