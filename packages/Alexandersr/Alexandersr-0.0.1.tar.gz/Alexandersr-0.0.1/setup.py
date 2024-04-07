from setuptools import setup


readme = open("./README.md", "r")
setup(
    name = 'Alexandersr',
    version = '0.0.1',
    description = 'Tarea de modulos de programacion II',
    long_description = readme.read(),
    author = 'Alexander Sanchez',
    author_email= 'alexadersr599@gmail.com',
    classifiers = [ ],
    keywords = ['testing', 'logging', 'example'],
    license = 'MIT',
    include_package_data = True
)

