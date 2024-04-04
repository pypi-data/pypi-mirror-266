from setuptools import find_packages, setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='pygnss',
    version_cc='{version}',
    author='Rokubun',
    author_email='info@rokubun.cat',
    description='Rokubun GNSS processing utilities.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='http://opensource.org/licenses/MIT',
    url="https://github.com/rokubun/pygnss",
    setup_requires=['setuptools-git-version-cc'],
    packages=["pygnss"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "docopt",
        "requests",
        "pytest",
        "pytest-mocha",
    ],
    entry_points={
        'console_scripts': [
        ]
    }
)
