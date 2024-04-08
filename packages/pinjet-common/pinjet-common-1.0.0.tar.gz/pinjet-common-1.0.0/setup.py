from setuptools import setup, find_packages


VERSION = '1.0.0'
DESCRIPTION = 'Common constants used throughout pinjet projects'
AUTHOR = 'abetrack3 (Abrar Shahriar Abeed)'
AUTHOR_EMAIL = '<abrarshahriar2361@gmail.com>'

setup(
    name='pinjet-common',
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'StrEnum'
    ],
)
