from setuptools import setup, find_packages

setup(
    author='Anna Movsisyan, Lusine Aghinyan, Ararat Kazarian, Hovhannes Hovhannisyan, Eduard Petrosyan',
    description='A package designed to efficiently generate new product combinations using check information, and deliver combo suggestions to business partners via email.',
    name='combogenius',
    version='0.1.0',
    packages=find_packages(include=['combogenius','combogenius.*']),
)