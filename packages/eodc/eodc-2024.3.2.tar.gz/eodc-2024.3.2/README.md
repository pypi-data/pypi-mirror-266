# EODC SDK
![PyPI - Status](https://img.shields.io/pypi/status/eodc)
![PyPI](https://img.shields.io/pypi/v/eodc)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eodc)

Python SDK for interacting with EODC services.

## Installation
Install the SDK with pip:

```
pip install eodc
```

## Usage
### Dask Clusters

```
from eodc import settings
from eodc.dask import EODCCluster

settings.DASK_URL = "<EODC dask gateway endpoint>"

cluster = EODCCluster()
```

### Function-as-a-Service (FaaS)
TODO
