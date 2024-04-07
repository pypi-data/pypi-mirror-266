# Python Async API Client

This have in mind to start developing API clients for Home Assistant to be 100% asynchronous

## How to Use it?

Fork this repository by using it as a template.

## Structure

This package provides good defaults for any API client code that is split on the following modules:

-   **`errors.py`**: module that define the custom errors the API and/or client would be returning to their users.
-   **`model.py`**: definition of the API data model. All returned objects from the clients would be defined here.
-   **`client.py`**: the logic around calling the API

## Development

To start developing with this package, fork it, create a virtual environment and install all the dependencies needed for development.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install '.[dev]'
```

## Best Practices

This package provides already an skeleton with some best practices when starting developing your API client.

1.  100% async from the start: Home Assistant runs its main logic using an asynchronous engine, and having 3rd party clients running async can have performance benefits and ease of integration on new and existing components.
2.  A `aiohttp.ClientSession` should always to be a constructor argument (so a session and connection pool can be shared between multiple clients). The template already provides a class constructor to create the Client without any initial `ClientSession` in case it is not available.
3.  The output of each API endpoint is a typed `Model` that is build as a dataclass and can be parsed from a JSON response or a nested dictionary. This ensures the consumer of the API outputs can take benefits from the benefits dataclasses provide like readaibility on its structure and field types.
4.  The whole library is annotated with Python types so type checkers can help us detect errors early on rather than at runtime.
