from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='c4p',  # required
    version='2024.4.5',
    description='c4p: CESM for Paleo',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Feng Zhu, Jiang Zhu',
    author_email='fengzhu@ucar.edu, jiangzhu@ucar.edu',
    url='https://github.com/fzhu2e/cesm4paleo',
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/c4p'],
    package_data={'': ['src']},
    license='MIT',
    zip_safe=False,
    keywords='CESM, paleoclimate',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    install_requires=[
        'colorama',
        'tqdm',
        'xarray',
        'netCDF4',
        'nc-time-axis',
        'dask',
        'sh',
        'pygplates',
    ],
)
