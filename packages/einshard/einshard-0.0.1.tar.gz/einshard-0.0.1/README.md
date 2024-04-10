# Einshard

High-level array sharding API for JAX

## Installation

This library requires at least Python 3.12.

```sh
pip install einshard
```

## Usage

```python
# initialising JAX CPU backend with 16 devices
n_devices = 16
import os
os.environ['JAX_PLATFORMS'] = 'cpu'
os.environ['XLA_FLAGS'] = os.environ.get('XLA_FLAGS', '') + f' --xla_force_host_platform_device_count={n_devices}'

from einshard import einshard
import jax
import jax.numpy as jnp

a = jnp.zeros((4, 8))
a = einshard(a, 'a b -> * a* b2*')
jax.debug.visualize_arra
```

## Development

```sh
python3.12 -m venv venv
. venv/bin/activate
```

```sh
pip install -U pip
pip install -U wheel
pip install "jax[cpu]"
pip install -r requirements.txt
```

Run test:

```sh
python tests/test_einshard.py
```

Build package:

```sh
python -m build
```
