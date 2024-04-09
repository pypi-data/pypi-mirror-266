from setuptools import setup, find_packages

setup(
    name='meldrx_fhir_client',
    description='A simple FHIR client for MeldRX.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/darena-solutions/meldrx-client-py',
    version='0.0.8',
    author='EM',
    author_email='eric@darenasolutions.com',
    packages=find_packages(),
    install_requires=[],
    tests_require=['pytest'],
    test_suite='tests',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
