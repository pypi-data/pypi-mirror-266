from setuptools import setup, find_packages


install_requires = [
]

setup(
    name='importer',
    version='1.0',
    author='GrowingIO',
    packages=find_packages(include=["importer*"]),
    install_requires=install_requires
)
