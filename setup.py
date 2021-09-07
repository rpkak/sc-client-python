import os
from setuptools import find_packages, setup


def get_requirements():
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
        return f.readlines()


setup(
    name='sc-client',
    version='0.0.1-alpha.1',
    packages=find_packages(),
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'scpy = sc_client.cli:scpy'
        ]
    }
)
