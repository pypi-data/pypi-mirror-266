# PyBob

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

PyBob is an unofficial python SDK for the [Bob](https://www.hibob.com/) [API](https://apidocs.hibob.com/)

### Initialise

```bash
pip install pybob-sdk
```

```python
from pybob_sdk import Bob

bob = Bob(
    service_account_id="YOUR_SERVICE_ACCOUNT_ID_HERE"
    service_account_token="YOUR_SERVICE_ACCOUNT_TOKEN_HERE"
)
```

### Examples

Company search

```python

# Search company people
employee = bob.people.search(
    fields=["root.id", "root.fullName", "root.email"],
    filters=[{
        "fieldPath": "root.email",
        "operator": "equals",
        "values": ["anakin.skywalker@company.com"]
        }]
)

print(employee)

```

Output

```bash
{ 'employees' : [
    {
    'fullName': 'Anakin Skywalker', 
    '/root/email': {
        'value': 'anakin.skywalker@company.com'
        }, 
    '/root/fullName': {
        'value': 'Anakin Skywalker'
        }, 
    'email': 'anakin.skywalker@company.com', 
    '/root/id': {
        'value': '123456789'
        }, 
    'id': '123456789'
        }
    ] 
}
```

Employment history

```python
# List employment history
results = bob.people.employee.list_employment_history(
    employeeId="123456789"
)

working_pattern = results["values"][0]["workingPattern"]["days"]

for day, hours in working_pattern.items():
    print(f"{day}: {hours}")
```

Output

```bash
monday: 7
tuesday: 7
wednesday: 7
thursday: 7
friday: 7
saturday: 0
sunday: 0
```