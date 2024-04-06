# setup.py
from setuptools import setup, find_packages

setup(
    name='RakHubAPI',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='azim0ff',
    author_email='azimoff@azimoff.online',
    description='Библиотека для работы с API RakHub, позволяющая удобно запускать RakBot сессии на игроков San Andreas Multiplayer (SAMP).',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/azim00ff/RakHubAPI/',
)