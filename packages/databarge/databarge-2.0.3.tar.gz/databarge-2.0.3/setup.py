from setuptools import setup 

with open("README.md", 'r') as f:
    long_description = f.read()

setup( 
    name='databarge', 
    version='2.0.3', 
    description='Simple ETL tools for SQL Server',
    author='Porte Verte', 
    author_email='porte_verte@outlook.com', 
    url='https://github.com/porteverte/databarge',
    packages=['databarge'],
    package_dir={'':'src'},
    python_requires=">=3.8",
)