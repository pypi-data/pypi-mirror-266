from setuptools import setup, find_packages


setup(
    name='PheTK',
    version='0.1.37',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    package_data={
        '': ['*.*'],
        'PheTK': ['phecode/*'],
    },
    url='https://github.com/nhgritctran/PheTK',
    license='GPL-3.0',
    author='Tam Tran',
    author_email='PheTK@mail.nih.gov',
    description='The Phenotype Toolkit',
    install_requires=[
        "adjusttext",
        "connectorx",
        "google-cloud-bigquery",
        "hail",
        "lifelines",
        "matplotlib",
        "numpy",
        "pandas",
        "polars",
        "pyarrow",
        "statsmodels",
        "tqdm"
    ]
)
