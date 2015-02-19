pyinsightly: Python library for Insightly API
=============================================

Example
-------
```python
import datetime
from insightly import Insightly
i = Insightly(my_api_key)

# Get a list of organizations and order by date created descending
yesterday = datetime.datetime.now() - datetime.timedelta(hours=24)
res = i.list('organisations', DATE_CREATED_UTC__gt=yesterday,
             order_by=('-DATE_CREATED_UTC',))

# Create a new org
res = self.add('organisations', {'ORGANISATION_NAME': 'Test'})
org_id = res['ORGANISATION_ID']

# Update it
res = self.update('organisations', {'ORGANISATION_NAME': 'Still Test'})

# Retrieve it
res = self.get('organisations', org_id)

# Delete it
self.delete('organisations', org_id)
```

Install
-------
```bash
pip install git+https://github.com/jfialkoff/pyinsightly.git
```

Debugging
---------
If Insightly responds with an error, you can turn debugging on to check
the request:
```python
i = Insightly(my_api_key, debug=True)
```

Testing
-------
You can easily run a suite of basic tests that perform a CRUD operation
on organizations. Please note that this operation will create a new
organization in Insightly called "pyinsightly test" which is later
deleted. You will need the necessary permissions in order to execute
these actions. To run the tests, simply run:
```python
from insightly import Insightly
i = Insightly(my_api_key)
i.test()
```
