# Fixpoint Python SDK

The `FixpointClient` wraps the OpenAI API Client. You can call it just like OpenAI API Client. The sdk will intercept calls to certain OpenAI APIs, record input / outputs and forward that information to Fixpoint's api server.

## Installation

You can view the package on [pypi](https://pypi.org/project/fixpoint-sdk/). To install:

`pip install fixpoint-sdk`

## Usage

To use the sdk make sure that you have the following variables set in your environment: `FIXPOINT_API_KEY` and `OPENAI_API_KEY`.

## Development

### Virtual Env

To create a virtual environment called `venv` from your terminal run `python3 -m venv venv`.

#### Activate

`source venv/bin/activate`

#### Install packages

To install the package locally for development:

```
# in "editable mode" so your install changes as you update the source code:
pip install -e .

# and to install dev dependencies
pip install -e '.[dev]'
```

If you get an error like:

> ERROR: File "setup.py" not found. Directory cannot be installed in editable mode: /home/dbmikus/workspace/github.com/gofixpoint/python-sdk
> (A "pyproject.toml" file was found, but editable mode currently requires a setup.py based build.)

Try upgrading pip and retrying:

```
pip install --upgrade pip
pip install -e .
```


In general, you should not install from the `requirements.txt` file, instead
following the installation method suggested above.

#### Deactivate

`deactivate`

### Git hooks

Set up your Githooks via:

```
git config core.hooksPath githooks/
```

## Examples

You can find examples of how to use the API in `examples`.
