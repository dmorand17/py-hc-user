from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    requirements = [req for req in f.read().splitlines() if not req.startswith('#')]
setup(
    name='healthclouduser_builder',
    version='0.1.0',
    description='Create Healthcloud users from a csv',
    long_description=readme,
    author='Douglas Morand',
    author_email='dmorand@gmail.com',
    url='https://github.com/dmorand17/healthclouduser_builder',
    license=license,
    packages=find_packages(exclude=('tests', 'templates')),
    install_requires=requirements
)