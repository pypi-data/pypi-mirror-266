# prosto-sms | API python wrapper

## TODO
- tests
------

## Install
```shell
python -m pip install prosto_sms
```
------

## Examples
### Auth by key and get profile data:
```python
import prosto_sms

api = prosto_sms.api.API(
    key="bd...5bb"
)

print(api.methods.get_profile())
```

### Auth by creds and get profile data:
```python
import prosto_sms

api = prosto_sms.api.API(
    email="me@chydo.dev",
    password="password"
)

print(api.methods.get_profile())
```