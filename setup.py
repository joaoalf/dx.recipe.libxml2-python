# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

__author__ = 'joaoalf'

name = 'dx.recipe.libxml2_python'
setup(
    name = name,
    version = '0.1dev',
    description = "This is a recipe to generate libxml2 python's bindings egg.",
    author = 'João Alfredo Gama Batista',
    author_email = 'ermitaoj@gmail.com',
    package_dir = {'':'src'},
    packages = find_packages('src'),
    include_package_data = True,
    namespace_packages = ['dx', 'dx.recipe'],
    entry_points = {'zc.buildout':['default = %s:Recipe' % name]},
    zip_safe = False,
    install_requires = [
        'zc.buildout',
        'setuptools',
        'zc.recipe.egg',
        ],
)