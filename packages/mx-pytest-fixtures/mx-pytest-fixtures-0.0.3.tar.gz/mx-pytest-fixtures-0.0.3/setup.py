from setuptools import setup, find_packages

VERSION = '0.0.3'
DESCRIPTION = 'Test fixtures for pytest testing framework.'
LONG_DESCRIPTION = 'A package which provides fixtures for the pytest testing framework.'

# Setting up
setup(
    name="mx-pytest-fixtures",
    version=VERSION,
    author="Ismail Chbiki",
    author_email="is.chbiki@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'pytest', 'fixtures', 'testing'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)