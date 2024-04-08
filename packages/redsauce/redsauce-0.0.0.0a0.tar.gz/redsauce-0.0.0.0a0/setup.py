from setuptools import setup, find_packages

setup(
    name='redsauce',
    version='0.0.0.0-alpha',
    packages=find_packages(),
    install_requires=[
        'redis[hiredis]',
    ],
    tags=['redis', 'cache', 'queue', 'api', 'development'],
    author='Eric DiGioacchino',
    author_email='eric.digioacchino01@gmail.com',   
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)