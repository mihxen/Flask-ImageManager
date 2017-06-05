# coding: utf8

from setuptools import setup, find_packages

setup(
    name='Flask-ImageManager',
    license='BSD',
    description='Easy way to manage your images in Flask application.',
    long_description=open('README.md').read(),
    author='Mikhail Ksenofontov',
    author_email='mihx95@gmail.com',
    url='https://github.com/mihxen/Flask-ImageManager/',
    platforms='any',
    zip_safe=False,
    include_package_data=True,
    install_requires=['Flask', 'Flask-WTF'],
    packages=find_packages()
)
