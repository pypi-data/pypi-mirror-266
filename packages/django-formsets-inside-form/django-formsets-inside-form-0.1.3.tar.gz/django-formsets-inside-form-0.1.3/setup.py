from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='django-formsets-inside-form',
    version='0.1.3',
    description='A library to handle formsets within forms in Django',
    long_description=long_description,  
    long_description_content_type="text/markdown", 
    author='Deivid Hugo',
    author_email='deividhugoof@gmail.com',
    url='https://github.com/DeividHugo/django-formsets-inside-form',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'Django>=2.0',
    ],
)
