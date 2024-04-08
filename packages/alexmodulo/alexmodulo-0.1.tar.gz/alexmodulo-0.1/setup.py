from setuptools import setup

readme = open("./README.md", "r")

setup(
    name = 'alexmodulo',
    version = '0.1',
    description = 'Tarea de modulos de programacion II',
    long_description = readme.read(),
    long_description_content_type='text/markdown',
    author = 'Alexander Sanchez',
    author_email= 'alexadersr599@gmail.com',
    classifiers = [ ],
    license = 'MIT',
    include_package_data = True
)

