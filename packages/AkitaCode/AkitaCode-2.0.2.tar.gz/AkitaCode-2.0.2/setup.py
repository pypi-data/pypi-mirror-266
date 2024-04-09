from setuptools import setup, find_packages

setup(
    name='AkitaCode',
    version='2.0.2',
    packages=find_packages(),
    install_requires=[
        'python-can==4.2.2',
    ],
    url='https://github.com/alexamatausa/akitacode',
    license='MPL',
    author='Àlex Amat Abad',
    author_email='amatabadalex@gmail.com',
    description='The AkitaCode parser and compiler.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)