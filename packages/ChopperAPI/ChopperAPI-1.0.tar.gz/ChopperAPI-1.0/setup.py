from setuptools import setup, find_packages

setup(
    name='ChopperAPI',
    version='1.0',
    author='1F2L',
    description="A package for 1F2L's web based chopperAPI",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://1f2l.us/api/chopper',
    packages=find_packages(), # find __innit__.py file
    python_requires='>=3.1',
    install_requires=[
        'requests>=2.25.1'
    ]
)
