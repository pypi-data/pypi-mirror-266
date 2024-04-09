from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='flask_sqlalchemy_magic_query',
    version='0.1.3.1',
    description='Converts HTTP URL query string parameters to flask_sqlalchemy query results',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/gabrielligoski/flask_sqlalchemy_magic_query',
    author='Gabriel Ligoski',
    author_email='gabriel.ligoski@gmail.com',
    license='MIT',
    packages=['flask_sqlalchemy_magic_query'],
    install_requires=['flask', 'sqlalchemy', 'flask_sqlalchemy']
)
