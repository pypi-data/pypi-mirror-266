# setup.py
from setuptools import setup, find_packages

setup(
    name='automation_tools',
    version='1.0.8',
    packages=find_packages(),
    install_requires=[
        'openpyxl',
    ],
    author='Omar Lydale Morrison',
    author_email='omar.morrison@sportyventures.com',
    description='A suite of automation tools for various tasks.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/sportyomar/automation_tools',
    license='MIT',
)




