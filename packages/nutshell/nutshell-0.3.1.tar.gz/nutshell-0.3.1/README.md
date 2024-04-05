# Nutshell API

This is a work-in-progress attempt at a pythonic API for querying the Nutshell CRM API. It does not yet support
modifying data in a Nutshell instance.

## Installation

```bash 
pip install nutshell
```

## Usage

- Initialize the API instance with your credentials
- Create an instance of the method(s) you want to call
- Pass a single method instance, or a collection of methods to the `api_calls` property of the API class
- Execute the method calls on API with the `call_api()` method
    - *aiohttp is used to make the API calls asynchronous*
- Unpack the results

```python
import os

from rich import print

import nutshell
from nutshell import methods

find_activities = methods.FindActivityTypes()
ns = nutshell.NutshellAPI(os.getenv("NUTSHELL_USERNAME"), password=os.getenv("NUTSHELL_KEY"))
ns.api_calls = find_activities
activity_types = ns.call_api()
print(activity_types)
```

Results are returned as a list of namedtuples with fields `method` and `response`. and all responses have a `result`
attribute that contains the data returned by the API.

```python
[
    MethodResponse(
        method=FindActivityTypes(
            api_method='findActivityTypes',
            order_by='name',
            order_direction='ASC',
            limit=50,
            page=1,
            params={
                'orderBy': 'name',
                'orderDirection': 'ASC',
                'limit': 50,
                'page': 1
            }
        ),
        response=FindActivityTypesResult(
            result=[
                ActivityType(
                    stub=True,
                    id=1,
                    rev='1',
                    entity_type='Activity_Types',
                    name='Phone Call / Meeting'
                ),
                ActivityType(
                    stub=True,
                    id=3,
                    rev='3',
                    entity_type='Activity_Types',
                    name='Email/Log'
                ),
            ]
        )
    )
]
```

## TODO

- Gracefully handle errors on method queries
- Convenience methods for common queries (Users, Leads, etc.)