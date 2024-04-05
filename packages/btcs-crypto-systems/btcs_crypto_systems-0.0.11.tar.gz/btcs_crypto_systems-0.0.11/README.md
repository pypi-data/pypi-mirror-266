# crypto systems package for BTCS crypto business systems


### Install
```bash
pip install btcs_crypto_systems
```

### Update
```bash
pip install btcs_crypto_systems --upgrade
```
## Usage

### TokenMaster
```python
from btcs_crypto_systems import token_master

tm = token_master.TokenMaster(env="test")
print(tm.assets[7].symbol)
```

### Utils
```python
from btcs_crypto_systems import utils

csv_writer = utils.get_csv_writer(file_name="example_output_file", headers=["address", "balance"])
csv_writer.writerow(["0x8c8d7c46219d9205f056f28fee5950ad564d7465","1.001"])

#creates a file called 20230217_0853_example_output_file.csv
```

### AMS
```python
from btcs_crypto_systems import address_manangement_service

ams = address_manangement_service.AMS(env="test")
print(json.dumps(ams.get_addresses(is_deposit=True, include_balances=True, limit=10, tags=["siba"]), indent=2))
```


## Update the package
Navigate to the folder where the pyproject.toml file is. Update version number.
```bash
python3 -m build
python3 -m twine upload --repository pypi dist/*
```

Make sure old bulds are not part of the dist folder.

```
username: __token__
password: get an API key from here https://pypi.org/manage/account/token/ 
```
