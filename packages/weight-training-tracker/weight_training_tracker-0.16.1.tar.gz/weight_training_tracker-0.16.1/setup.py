#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=7.0',
    "pyfiglet",
    "PyYAML",
    "Pydantic",
    "Rich",
    "termcolor",
]

test_requirements = [ ]

setup(
    author="Jaideep Sundaram",
    author_email='jai.python3@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A simple CLI-based app for tracking weight training.",
    entry_points={
        'console_scripts': [
            'weight-training-tracker=weight_training_tracker.main:main',
            'weight-training-tracker-summarize=weight_training_tracker.summarize_workout_session:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='weight-training-tracker',
    name='weight_training_tracker',
    packages=find_packages(include=['weight_training_tracker', 'weight_training_tracker.*']),
    package_data={"weight_training_tracker": ["conf/config.yaml"]},
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/jai-python3/weight-training-tracker',
    version='0.16.1',
    zip_safe=False,
)
