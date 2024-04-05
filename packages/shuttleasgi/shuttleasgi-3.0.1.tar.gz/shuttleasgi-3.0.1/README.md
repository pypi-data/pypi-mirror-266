[![Build](https://github.com/Neoteroi/BlackSheep/workflows/Main/badge.svg)](https://github.com/Neoteroi/BlackSheep/actions)
[![pypi](https://img.shields.io/pypi/v/BlackSheep-Shuttle.svg?color=blue)](https://pypi.org/project/BlackSheep-Shuttle/)
[![versions](https://img.shields.io/pypi/pyversions/blacksheep-shuttle.svg)](https://github.com/herumes/blacksheep-shuttle)
[![codecov](https://codecov.io/gh/Neoteroi/BlackSheep/branch/master/graph/badge.svg?token=Nzi29L0Eg1)](https://codecov.io/gh/Neoteroi/BlackSheep)
[![license](https://img.shields.io/github/license/Neoteroi/blacksheep.svg)](https://github.com/Neoteroi/blacksheep/blob/main/LICENSE) [![Join the chat at https://gitter.im/Neoteroi/BlackSheep](https://badges.gitter.im/Neoteroi/BlackSheep.svg)](https://gitter.im/Neoteroi/BlackSheep?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![documentation](https://img.shields.io/badge/📖-docs-purple)](https://www.neoteroi.dev/blacksheep/)

# BlackSheep-Shuttle
BlackSheep-Shuttle is a fork of [BlackSheep](https://github.com/Neoteroi/BlackSheep) with numerous fixes, improvements, and new features.

Credits to [RobertoPrevato](https://github.com/robertoprevato) for creating the original masterpiece.

```ShellSession
pip install -U blacksheep-shuttle
```

## Building
Helpful commands for building and testing the project yourself.
*Using mingw32k-make for Windows*
### Make
```ShellSession
mingw32-make compile
```
### Build
```ShellSession
mingw32-make build
```
### Prepare for publishing
```ShellSession
mingw32-make prepforbuild
```
### Create dist
```ShellSession
python -m build
```
### Clean (Optional)
```ShellSession
mingw32-make clean
```
### Uploading to PyPi
```ShellSession
twine upload -r pypi dist/*
```