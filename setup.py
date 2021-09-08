import os
from setuptools import find_packages, setup


def get_requirements():
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
        return f.readlines()


setup(
    name='sc-client',
    version='1.0.0',
    packages=find_packages(),
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'scpy = sc_client.cli:scpy'
        ]
    }
)
