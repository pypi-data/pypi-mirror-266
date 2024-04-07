from setuptools import setup, find_packages


def get_version():
    for line in open('istari/__init__.py', 'r'):
        if line.startswith('__version__'):
            return line.split("'")[1]


setup(
    name='istari',
    version=get_version(),
    author='Janus Digital LLC',
    author_email='justice@janusdigital.io',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'istari=istari.cli:main',
        ],
    },
)
