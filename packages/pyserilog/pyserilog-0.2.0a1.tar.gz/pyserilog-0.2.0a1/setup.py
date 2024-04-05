"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# To use a consistent encoding
from codecs import open

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# Get the long description from the README file
with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="pyserilog",

    version="0.2.0a1",

    description="python version of serilog a structured logging library",
    long_description=long_description,
    author='Reza Sadeghi',
    author_email='rezasadeghikhas@gmail.com',
    license="Apache2",

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: System :: Logging',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet :: Log Analysis',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.11',
    ],

    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["tests*", "test_dummies"]),
    install_requires=[
        "multipledispatch>=1.0.0"
    ]

)
