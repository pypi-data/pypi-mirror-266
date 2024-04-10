from io import open
from setuptools import setup

version = '1.0.8'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='BrightnessBooster',
    version=version,

    author='necros2604',
    author_email='bair1hasykov@gmail.com',

    description=(
        u'The code enhances an image\'s brightness and contrast'
    ),
    
    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=['BrightnessBooster'],
    install_requires=['scipy', 'numpy']

)