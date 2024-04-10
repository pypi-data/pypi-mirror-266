from setuptools import setup

r = open("./README.md", "r")

setup(

    name= 'moduloprueba',
    packages= ['moduloprueba'],
    version= '0.1',
    description= 'Trabajo de modulos',
    long_description= r.read(),
    long_description_content_type= 'text/markdown',
    author= 'oscarchungara',
    author_email= 'oscarunoja20@gmail.com',
    classifiers= [],
    license= 'MIT',
    include_package_data= True
)