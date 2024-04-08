from setuptools import setup, find_packages

setup(
    name='openai_cost_logger',
    version='0.0.2',
    description='OpenAI Cost Logger',
    author='Lorenzo Drudi | Mikolaj Boronski | Ivan Zakazov',
    author_email='lorenzodrudi11@gmail.com',
    license='MIT',
    packages=find_packages(include=['openai_cost_logger', 'openai_cost_logger.*']),
    requires=['openai', 'pandas', 'matplotlib'],
    install_requires=['openai', 'pandas', 'matplotlib'],
)