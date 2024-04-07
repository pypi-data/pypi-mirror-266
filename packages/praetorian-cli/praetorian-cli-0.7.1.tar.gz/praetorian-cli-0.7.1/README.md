# Praetorian CLI

The CLI is a fully-featured companion to the Chaos UI, which is hosted at research.praetorian.com.

## Install

Python 3.8+ and PIP are required.

```zsh
pip install praetorian-cli
```

## Usage

To use the CLI:

1. Register for an account at chaos.praetorian.com.
2. Log in and download your keychain file to ``~/.praetorian/keychain.ini``.

View help for all available commands:

```zsh
praetorian chaos --help
```

The CLI is configured as a simple command + option utility. For example, to retrieve all assets in your account simply run:

```zsh
praetorian chaos assets
```

## Developers

Integrate the CLI into your own application:

1. Include the dependency ``praetorian-cli`` in your project
2. Import the Chaos class ``from praetorian_cli.sdk.chaos import Chaos``
3. Import the Keychain class ``from praetorian_cli.sdk.keychain import Keychain``
4. Call any function (example below)

### Example

```python
from praetorian_cli.sdk.chaos import Chaos
from praetorian_cli.sdk.keychain import Keychain

chaos = Chaos(Keychain(profile='United States'))
chaos.add_seed('example.com')
```
