# Development guide

We welcome new contribution!
Please feel free to open pull-requests and/or issues.
If you are not sure what to do,
file an [issue on GitHub](https://github.com/RIMS-Code/RIMSSchemeDrawer/issues)
and we can discuss it there.

Contributions do not only have to be in the form of code.
We also welcome contributions in the form of documentation, etc.!

Below are some guidelines/rough instructions on how this project is set up.
If you have any questions, please raise them!

## Configuration

The `RIMSSchemeDrawer` package is configured to use
[`rye`](https://rye-up.com/) for the development environment.
If you have `rye` installed, clone the repo and then run

```bash
rye sync --aditional-features
```

to get the full development environment setup.

## Pre-commit hooks

We use [`pre-commit`](https://pre-commit.com/) hooks in order to ensure
code formatting and linting prior to committing. To install the hooks, run

```bash
pre-commit install
```

!!! note
    In order for this to work, you must have `pre-commit` itself installed.
    If you use `rye`, you can simply install it by running

    ```bash
    rye install pre-commit
    ```

## Testing

We use `pytest` for testing. To run the tests, simply run

```bash
rye run test
```

## Documentation

Please ensure that all features, etc., are documented.
The documentation is built using `mkdocs` and `mkdocstrings`.
To check the documentation locally,
run

```bash
rye run mkdocs serve
```

and then open your browser at `http://localhost:8000`.
You should see the documentation there.

Upon a pull-request,
the documentation is also created using a readthedocs webhook.
You can see the documentation by clicking on the appropriate check in the pull-request.

## Formatting and linting

We use [`ruff`](https://astral.sh/ruff) for formatting and linting.
You can run `ruff` directly from `rye`:

```bash
rye fmt
rye lint
```

This will run the formatter (first line)
and the linter (second line).
