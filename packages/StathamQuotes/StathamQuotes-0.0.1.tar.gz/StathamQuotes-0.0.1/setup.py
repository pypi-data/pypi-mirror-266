from setuptools import setup

version = "0.0.1"

setup(
    name='StathamQuotes',
    version=version,
    description='A useful module',
    author='gbu1at',
    author_email='bulatchess@mail.ru',
    packages=['StathamQuotes'],  # same as name
    install_requires=['random'],  # external packages as dependencies
)
