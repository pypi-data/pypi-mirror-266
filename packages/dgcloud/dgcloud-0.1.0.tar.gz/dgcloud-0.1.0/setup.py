from setuptools import setup, find_packages

setup(
    name='dgcloud',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'pyyaml',
        'paramiko',
    ],
    entry_points={
        'console_scripts': [
            'dgcloud=dgcloud.cli:main',
        ],
    }
)
