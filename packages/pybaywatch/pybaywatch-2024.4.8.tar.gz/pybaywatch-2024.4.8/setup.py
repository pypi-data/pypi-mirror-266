from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='pybaywatch',  # required
    version='2024.4.8',
    description='PyBAYWATCH: BAYWATCH in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Feng Zhu, Jessica Tierney',
    author_email='fengzhu@ucar.edu, jesst@arizona.edu',
    url='https://github.com/fzhu2e/pybaywatch',
    packages=find_packages(),
    license='MIT',
    zip_safe=False,
    keywords='Bayeisan Hierarchical Proxy System Models for Sediments',
    classifiers=[
        'Programming Language :: Python :: 3.11',
    ],
    include_package_data=True,
    install_requires=[
        'colorama',
        'oct2py',
    ],
)
