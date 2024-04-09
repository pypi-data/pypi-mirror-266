#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = ['teradataml>=17.10.00.02',
                'pandas',
                'numpy',
                'scikit-learn>=1.3.0'
                ]

extras_require = {
    'plot': ["plotly>=5.0", "seaborn>=0.11"]
}

# test_requirements = ['pytest>=3', ]

setup(
    name='tdprepview',
    version='1.4.0',
    description="Python Package that creates Data Preparation Pipeline in Teradata-SQL in Views",

    author="Martin Hillebrand",
    author_email='martin.hillebrand@teradata.com',

    packages=find_packages(include=['tdprepview', 'tdprepview.*']),

    python_requires='>=3.8',
    install_requires=requirements,
    extras_require=extras_require,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Database',
    ],
    keywords='tdprepview,teradata,database,preprocessing,data engineering,data science',

    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    include_package_data=True,

    # test_suite='tests',
    # tests_require=test_requirements,
    # url='https://',

    zip_safe=False,
)
