from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='artice',
    version='0.0.1',
    packages=find_packages(),
    install_requires=required,
    description='Twisting the magic of financial prices and articles',
    author='Steve Flyer',
    author_email='steveflyer7@gmail.com',
    license='MIT',
    include_package_data=True,
)
