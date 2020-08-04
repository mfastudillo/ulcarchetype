# ulcarchetype

ulcarchetype is a Python library that provides some simple tools to characterize the uncertainty due to archetype "underspecification" in life cycle assessment. Is meant to be used with the LCA software Brightway2. 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install ulcarchetype

```bash
pip install .
```

## Usage

```python
import brightway2 as bw
from ulcarchetype.utils import get_cf_info,minmax_archetype,cf_add_uncertainty

method = bw.methods.random()
cf_df = get_cf_info(method) # returns a dataframe with data on characterisation factors
minmax_archetype(cf_df) # returns a dataframe with data needed to define uncertain CFs
# or simply
cf_add_uncertainty(method) # returns a list of CFs taking into account archetype uncertainty
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[BSD 3-Clause License]