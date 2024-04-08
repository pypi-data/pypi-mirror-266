
from setuptools import setup, find_packages

setup(
    name='trialforrjhnjtj',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'kivy'

    ],
    entry_points={
        'console_scripts': [
            'hello_world_app = trialforrjhnjtj.main:main',
        ],
    },
)
