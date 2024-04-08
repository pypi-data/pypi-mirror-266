# s6r-hubspot

## Installation

```bash
    pip install s6r-hubspot
```

## Usage

```python
from s6r_hubspot import HubspotConnection

hubspot = HubspotConnection('your_access_token')
owners = hubspot.get_owners()
```


### Unit tests

To run unit_test file, you need to set up a token of an empty hubspot base in an environnement variable name 
HUBSPOT_TOKEN:
```bash
    export HUBSPOT_TOKEN='your_token'
```


## License

This project is licensed under the [GNU Lesser General Public License (LGPL) Version 3](https://www.gnu.org/licenses/lgpl-3.0.html).


## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements,
please open an issue or submit a pull request.

- GitHub Repository: [ScalizerOrg/s6r-hubspot](https://github.com/ScalizerOrg/s6r-hubspot)


## Contributors

* David Halgand - [GitHub](https://github.com/halgandd)
* Morgane Goujon - [GitHub](https://github.com/MorganeGoujon)
* Khalid Bentaleb - [GitHub](https://github.com/kbentaleb)
* Michel Perrocheau - [GitHub](https://github.com/myrrkel)


## Maintainer

This software is maintained by [Scalizer](https://www.scalizer.fr).


<div style="text-align: center;">

[![Scaliser](./logo_scalizer.png)](https://www.scalizer.fr)

</div>