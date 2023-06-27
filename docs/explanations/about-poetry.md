# About Poetry

As the website of [pytest](https://python-poetry.org/) mentions:

!!! quote
    Python packaging and dependency management made easy.

## How and why do we use Poetry

We use Poetry to manage some of our project's dependencies.

We use Poetry instead of pip because it saves all dependencies and transversal dependencies
in a dedicated lock file to ensure reproducibility on every system.

## Install Poetry

Install Poetry with the following command:

```sh title="In a terminal, execute the following command(s)."
pip install poetry
```

## Configuration

The configuration for Poetry is located in the `pyproject.toml` configuration file.

## Common tasks

### Enable a Python virtual environment

You can enable a Python virtual environment with the following command:

```sh title="In a terminal, execute the following command(s)."
poetry shell
```

# Install dependencies

You can install all dependencies in the Python virtual environment with the following command:

```sh title="In a terminal, execute the following command(s)."
poetry install
```

## Resources and alternatives

These resources and alternatives are related to the current item (in alphabetical order).

- [Effective Python Testing With Pytest](https://realpython.com/pytest-python-testing)
- [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/)
