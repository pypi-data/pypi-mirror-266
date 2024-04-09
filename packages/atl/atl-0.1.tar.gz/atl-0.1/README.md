# README

> ambedded.ch ambedded-technology-lab python3 library

## TODO

- search for all TODO

## basic construct

TODO

```bash
my_package/
│
├── module1/
│   ├── __init__.py
│   └── functions1.py
│
├── module2/
│   ├── __init__.py
│   └── functions2.py
│
├── main.py
│
└── setup.py
```

## Building and Testing Locally

Before deploying, it's a good idea to test your package locally. You can do this by installing it in editable mode:

```bash
python3 -m venv .venv
. ./.venv/bin/activate
pip3 install -e .
python3 main.py
```

## Deploying to PyPI

To deploy your package to PyPI, you'll need to register an account on the PyPI website if you haven't already. Once registered, you can use twine to upload your package.

First, install twine if you haven't already:

```bash
python3 -m venv .venv
. ./.venv/bin/activate
pip3 install twine
python3 setup.py sdist bdist_wheel
twine upload dist/*
```