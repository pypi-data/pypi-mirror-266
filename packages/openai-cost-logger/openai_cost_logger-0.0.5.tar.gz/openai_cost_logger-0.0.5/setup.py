from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='openai_cost_logger',
    version='0.0.5',
    description='OpenAI Cost Logger',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Lorenzo Drudi | Mikolaj Boronski | Ivan Zakazov',
    author_email='lorenzodrudi11@gmail.com',
    license='MIT',
    packages=find_packages(include=['openai_cost_logger', 'openai_cost_logger.*']),
    requires=['openai', 'pandas', 'matplotlib'],
    install_requires=['openai', 'pandas', 'matplotlib'],
    url='https://github.com/drudilorenzo/openai-cost-tracker'
)