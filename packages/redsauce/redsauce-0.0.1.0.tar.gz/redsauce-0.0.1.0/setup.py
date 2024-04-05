from setuptools import setup, find_packages

setup(
    name='redsauce',
    version='0.0.1.0',
    packages=find_packages(),
    install_requires=[
        'redis[hiredis]',
    ],
    tags=['redis', 'cache', 'queue', 'api', 'development'],
    author='Eric DiGioacchino',
    author_email='eric.digioacchino01@gmail.com',   
    long_description='Simplify Redis Cache/Queue API development by spreading the sauce.'
)