# ulcarchetype

ulcarchetype is a Python library that provides some simple tools to characterize the uncertainty due to archetype "underspecification" in life cycle assessment (i.e. when the "subcompartment" is not specified). It is meant to be used with the LCA software [Brightway2](https://brightway.dev/).

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install ulcarchetype

```bash
pip install ulcarchetype
```

## Usage

```python
import bw2data as bwd
from ulcarchetype.ulcarchetype import LCIAMethod


method_original = bwd.Method(('name of method without uncertainty',))

# transform impact assessment method
method_u = LCIAMethod(method_original)
method_u.transform_method(m)
method_u.set_uncertainty_type(4) # 4 represents uniform, other values are possible
cfs = method_u.build_cf_list() # list of characterisation factors

# register new version of the method 
new_method = bwd.Method(('name of method with uncertainty',))
new_method.register(description='version accounting for uncertainty in undefined archetypes')
new_method.write(cfs)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
BSD 3-Clause License