# Meshtastic Communicator (Backend)

This software pairs with the [Meshtastic Communicator Website](https://github.com/jrddunbr/MeshtasticCommunicatorWebsite)
to create a web interface for interacting with Meshtastic devices connected over USB/Serial.

## Development

It's pretty simple to set up a development environment:

```shell
python -m venv venv
source ./venv/bin/Activate
python -m pip install flask meshtastic flask_cors
```

## Run

If you haven't already started the Python venv, start that first.

Flask will start listening on port 5643
Do note the default CORS configuration is `*`

```shell
source ./venv/bin/Activate
python main.py
```
