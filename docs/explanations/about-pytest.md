# About pytest

As the website of [pytest](https://docs.pytest.org) mentions:

!!! quote
    The pytest framework makes it easy to write small, readable tests, and can scale to support complex functional testing for applications and libraries.

## How and why do we use pytest

We use pytest to test our services.

## Install pytest

Install pytest with the following command:

```sh title="In a terminal, execute the following command(s)."
pip install pytest pytest-cov
```

## Configuration

The configuration for pytest is located in the `pyproject.toml` configuration file.

## Common tasks

### Run the tests

Run the tests with the following command:

```sh title="In a terminal, execute the following command(s)."
pytest
```

### Run the tests with console output

By default, pytest hides outputs to the console. To display all outputs, run pytest with the following command:

```sh title="In a terminal, execute the following command(s)."
pytest --capture=no

# or

pytest -s
```

## Resources and alternatives

These resources and alternatives are related to the current item (in alphabetical order).

- [Effective Python Testing With Pytest](https://realpython.com/pytest-python-testing)
- [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/)
