# Nutshell API

This is a work-in-progress attempt at a pythonic API for querying the Nutshell CRM API. It does not yet support
modifying data in a Nutshell instance.

## Installation

```bash 
pip install nutshell
```

## Usage

This package includes four primary modules

- methods: provides Pydantic models for a selection of Nutshell API methods
    - model naming aligns with the API method names
- responses: Pydantic models for the responses returned by the API
    - response models are names with the API method name followed by "Result" (e.g. FindActivityTypes*Result*)
- entities: enums and Pydantic models to facilitate method creation and parsing results
- NutshellAPI class: provides a means to batch query the API with multiple methods via asyncio
    - Must be instantiated with your Nutshell username and API key.

### General flow

- Instantiate API method calls and collect them in an iterable
- Instantiate NutshellAPI with your Nutshell credentials
- Pass the method calls iterable to the NutshellAPI instance
- Call the API
- Unpack the results

```python
import asyncio
import os

from rich import print
import nutshell as ns

single_call = ns.FindActivityTypes()

nut = ns.NutshellAPI(os.getenv("NUTSHELL_USERNAME"), password=os.getenv("NUTSHELL_KEY"))
nut.api_calls = [single_call]
call_response = asyncio.run(nut.call_api())

for call in call_response:
    print(call)
```

___
Results are returned as a list of tuples. The first element is the method instance, the second is the response.

```python
(
    FindActivityTypes(
        api_method='findActivityTypes',
        order_by='name',
        order_direction='ASC',
        limit=50,
        page=1,
        params={'orderBy': 'name', 'orderDirection': 'ASC', 'limit': 50, 'page': 1}
    ),
    FindActivityTypesResult(
        result=[
            ActivityTypes(stub=True, id=1, rev='1', entity_type='Activity_Types', name='Phone Call / Meeting'),
            ActivityTypes(stub=True, id=3, rev='3', entity_type='Activity_Types', name='Email/Log'),
        ]
    )
)
```

All responses have a `result` attribute that contains the data returned by the API. The data is returned as Pydantic
models based on the API method invoked.

## TODO

- Handle errors returned from API
- Convenience methods for common queries (Users, Leads, etc.)