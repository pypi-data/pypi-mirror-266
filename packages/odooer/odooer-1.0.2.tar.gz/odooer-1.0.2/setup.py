from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='odooer',
    version='1.0.2',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'odooer=odooer.create_module:main',
        ],
    },
    install_requires=[
        # List your project's dependencies here
    ],
    author='Muhammad Osama',
    author_email='ocama_aslam@outlook.com',
    description='A CLI tool for creating Odoo module boilerplate',
    keywords='Odoo CLI',
    long_description=long_description,  
    long_description_content_type='text/markdown',
)
