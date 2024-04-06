# Avassa Client Library - Python

Use this library to integrate with the Avassa APIs from Python.

## Features

The library consists of two modules.

### avassa_client

Functions for authentication using username/password as well as approle
credentials. Also contains a generic rest_get function that can be used to talk
to any API endpoint.

### avassa_client.volga

Asynchronous library based on the websockets module for connecting to
Volga topics.

## Use

The Avassa Client is published to
[PyPi](https://pypi.org/project/avassa-client/) and can be installed:
```shell
python3 -m pip install --upgrade avassa-client
```

See the Volga Applications how-to in the Avassa Documentation for
further information.

### Publishing on PyPI
See BUILD-PUBLISH.md
