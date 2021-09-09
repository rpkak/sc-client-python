import os

from setuptools import find_packages, setup


def get_requirements():
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
        return f.readlines()


def get_readme():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')) as f:
        return f.read()


setup(
    name='sc-client',
    version='1.0.0',
    packages=find_packages(),
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'scpy = sc_client.cli:scpy'
        ]
    },
    url='https://github.com/rpkak/sc-client-python',
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    project_urls={
        'Source': 'https://github.com/rpkak/sc-client-python',
        'Tracker': 'https://github.com/rpkak/sc-client-python/issues'
    },
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ]
)
