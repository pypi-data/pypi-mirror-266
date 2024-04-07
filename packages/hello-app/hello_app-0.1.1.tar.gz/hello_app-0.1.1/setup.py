from setuptools import setup, find_packages

setup(
    author="Curtis",
    name="hello_app",
    description="A simple hello world app",
    version="0.1.1",
    extras_require={
        'test': ['pytest'],
    },
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
)