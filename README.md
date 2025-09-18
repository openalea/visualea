# Visualea
[![Docs](https://readthedocs.org/projects/visualea/badge/?version=latest)](https://visualea.readthedocs.io/)
[![Build Status](https://github.com/openalea/visualea/actions/workflows/conda-package-build.yml/badge.svg?branch=master)](https://github.com/openalea/visualea/actions/workflows/conda-package-build.yml?query=branch%3Amaster)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License--CeCILL-C-blue)](https://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html)
[![Anaconda-Server Badge](https://anaconda.org/openalea3/visualea/badges/version.svg)](https://anaconda.org/openalea3/visualea)

![visualea main window](https://github.com/openalea/visualea/blob/master/doc/_static/visualea.png?raw=true "visualea main window")

## Software

### Authors

> -   Christophe Pradal

### Institutes

CIRAD / INRAE / inria

### Status

Python package

### License

CecILL-C

**URL** : <https://visualea.rtfd.io>

## About

OpenAlea.Visualea is the Visual Programming Environment of OpenAlea. It allows using OpenAlea packages 
without programming language knowledge and to build dataflow graphically.

## Installation 

### user mode

```bash
mamba create -n visualea -c openalea3 -c conda-forge openalea.visualea
mamba activate visualea
```

### for developer, in an existing environment

```bash
git clone 'https://github.com/openalea/visualea.git'
cd visualea
mamba install --only-deps -c openalea3 -c conda-forge openalea.visualea
pip install -e .[options]
```
`[options]` is optional, and allows to install additional dependencies 
defined in the `[project.optional-dependencies]` section of your 
pyproject.toml file (usually "dev", or "doc", ...)

### for developer, in a new clean isolated environment
```bash
mamba env create -f conda/environment.yml 
mamba activate visualea
```
