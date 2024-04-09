from setuptools import setup, find_packages

with open('README.md', 'r', encoding = 'utf-8') as f:
    long_description = f.read()

setup(
    name = "ANBUtils",
    version = '1.7.3',
    packages = find_packages(),
    author = 'Yafei Hou',
    author_email = 'redbson@gmail.com',
    url = 'https://github.com/redbson/ANBUtils',
    description = 'ANBUilts is a versatile Python package that offers a comprehensive set of utility functions and '
                  'tools for data analysis, database operations, and messaging integration.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    python_requires = '>=3.8',
    install_requires = [
        "matplotlib>=3.0.0",
        "numpy>=1.0.0",
        "pandas>=1.0.0",
        "pymongo>=4.0.2",
        "requests>=2.0.0",
        "matplotlib>=3.0.0",
        "psutil>=5.0.0",
    ]
)
