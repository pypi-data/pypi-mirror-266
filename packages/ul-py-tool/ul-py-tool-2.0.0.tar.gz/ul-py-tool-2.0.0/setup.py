from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ul-py-tool',
    version='2.0.0',
    description='Python ul py tool',
    author='Unic-lab',
    author_email='',
    url='https://gitlab.neroelectronics.by/unic-lab/libraries/common-python-utils/ul-py-tool.git',
    packages=find_packages(include=['ul_py_tool*']),
    platforms='any',
    package_data={
        '': [
            'conf/*',
        ],
        'ul_py_tool': [
            'py.typed',
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            'ulpytool=ul_py_tool.main:main',
        ],
    },
    include_package_data=True,
    install_requires=[
        "numpy==1.23.3",
        "pandas==2.2.1",
        "pydantic[mypy]==2.6.4",
        "PyYAML==6.0",
        "colored==2.2.4",
        "rich==12.6.0",
        "tomli==2.0.1",
        "requests==2.31.0",
        "deepdiff==6.7.1",

        "mypy==1.9.0",
        "types-pytz==2024.1.0.20240203",
        "types-pyyaml==6.0.11",
        "types-requests==2.31.0.4",
        "types-setuptools==69.2.0.20240317",
        "types-python-dateutil==2.9.0.20240316",
        "typing-extensions==4.3.0",
        "data-science-types==0.2.23",

        "black==24.3.0",
        "ruff==0.3.4",
        "isort[colors]==5.10.1",
        "yamllint==1.35.1",

        "pytest==8.1.1",
        "pytest-cov==5.0.0",
        "python-gitlab==4.4.0",
        "kubernetes==29.0.0",

        "wheel==0.37.1",
        "twine==5.0.0",
        "setuptools==63.4.2",
    ],
)
