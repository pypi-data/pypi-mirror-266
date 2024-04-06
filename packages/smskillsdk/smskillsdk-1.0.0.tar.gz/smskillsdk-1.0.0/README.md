# smskillsdk (Python)

The Skills Python SDK package contains data types for the session and execute endpoints specified within the Skills REST API, along with a range of utility functions for working with the memory data structure.

## Installation

This package is intended for use with Python 3.8 and above.

```
pip install smskillsdk
```

## Usage

### Accessing request/response models

The request/response models are implemented with [Pydantic](https://pydantic-docs.helpmanual.io/), a library which assists with validation and type-checking.

```python
from smskillsdk.models.api import (
    SessionRequest,
    SessionResponse,
    ExecuteRequest,
    ExecuteResponse
)
```

Sub-models used within these request and response models can also be imported using

```python
from smskillsdk.models.api import (
    Output,
    Intent,
    Memory,
    Variables
)
```

In general, a developer should implement separate handler functions for the session and execute endpoints which takes a `SessionRequest` or `ExecuteRequest` as an argument and returns a `SessionResponse` or `ExecuteResponse` respectively. These objects can be serialized to JSON and returned within the HTTP response body. An example implementation of a handler function for generating an `ExecuteResponse` and a route method is shown below.

```python
# execute endpoint handler containing response generation logic
def execute_handler(request: ExecuteRequest) -> ExecuteResponse:

    # response generation logic here

    variables = Variables(public={ "card": { ... }})

    output = Output(
        text="",
        variables=variables
    )

    response = ExecuteResponse(
        output=output,
        memory=[],
        endConversation=True,
    )

    return response

# route method (using FastAPI syntax)
@app.post("/execute", status_code=status.HTTP_200_OK, response_model=ExecuteResponse, response_model_exclude_unset=True)
def execute(request: ExecuteRequest):
    return execute_handler(request)
```

#### Deserializing requests

Python dictionary objects can be deserialized into models.

```python
raw_request = {
    "key": value,
    ...
}

request = ExecuteRequest(**raw_request)
```

Pydantic will throw a [`ValidationError`](https://pydantic-docs.helpmanual.io/usage/models/#error-handling) if any of the keys or value types does not match the expected keys and values.

#### Serializing responses

Pydantic models can be [converted](https://pydantic-docs.helpmanual.io/usage/exporting_models/) into JSON strings or dictionary objects.

```python
request = ExecuteRequest(**{'text': 1, 'projectId': '111', 'sessionId': '123', 'memory': []})

json_str = request.json()
dict_obj = request.dict()
```

### Working with memory

The memory field within the request and response models of the session/execute endpoints can be used to persist state between conversation turns and share information between skills within a single session.

The data structure is comprised of an array of `Memory` objects

```python
class Memory(BaseModel):
    name: str
    value: Any
    session_id: Optional[str]
    scope: Optional[MemoryScope] = None
```

where the `name` field acts as a key. The optional `session_id` field can be used to differentiate between objects having the same `name` value, while the optional `scope` field can be used to control whether objects are shared between skills or remain private to a single skill (the default scope is `MemoryScope.PRIVATE`). Setting `scope: MemoryScope.PUBLIC` will mean that this particular memory object will be viewable and editable by all skills within a particular session.

**Note that memory objects with the same name but different session ID/scope will be treated as unique.**

We offer a range of utility functions to work with the memory data structure which can be imported from `smskillsdk.utils.memory`

#### `serialize_memory(data: dict, session_id: Union[str, None] = None, scope: MemoryScope = MemoryScope.PRIVATE) -> List[Memory]`

Converts a Python dict into a list of Memory objects with an optional session ID and scope.

Arguments:
- `data: dict`: A Python dictionary to be converted; keys should be strings
- `session_id: str`: An optional session ID to be assigned to each `Memory` object
- `scope: MemoryScope`: An optional scope to determine if the memory objects should be able to be shared with other skills within the session (default: `MemoryScope.PRIVATE`)

Returns:
- `List[Memory]`: A list of `Memory` objects


#### `deserialize_memory(memories: List[Memory], session_id: Union[str, None] = None, scope: Union[MemoryScope, None] = None) -> Dict[str, Any]`

Converts a list of `Memory` objects into a Python dict, filtered using an optional session ID or scope value. If there are multiple valid memory objects with the same name, the value closest to the end of the `memories` list will be returned.

Arguments:
- `memories: List[Memory]`: A list of `Memory` objects to be converted
- `session_id: str`: If provided, will only deserialize `Memory` objects with a matching session ID
- `scope: MemoryScope`: If provided, will only deserialize memory objects with a matching scope (otherwise all memory objects will be treated as valid)

Returns:
- `Dict[str, Any]`

#### `set_memory_value(memories: List[Memory], key: str, value: Any, session_id: Union[str, None] = None, scope: MemoryScope = MemoryScope.PRIVATE) -> None`

Sets a value in a list of `Memory` objects corresponding to a key and optional session ID or scope. If an object with a matching key/session ID/scope exists, its value will be overwritten.

Arguments:
- `memories: List[Memory]`: The list of `Memory` objects which will be operated on
- `key: str`: The key to search for
- `value: Any`: The value to set
- `session_id: str`: If provided, only `Memory` objects with a matching session ID will be considered; if none are found, a new memory object with a session ID will be created
- `scope: MemoryScope`: If provided, only memory objects with a matching scope will be considered (defaults to `MemoryScope.PRIVATE`)

Returns:
- No return value, the list of `Memory` objects is modified in-place


#### `get_memory_value(memories: List[Memory], key: str, session_id: Union[str, None] = None, scope: Union[MemoryScope, None] = None) -> Tuple[bool, Any]`

Retrieves a value from a list of `Memory` objects corresponding to a key and optional session ID or scope value.

Arguments:
- `memories: List[Memory]`: The list of `Memory` objects to be searched
- `key: str`: The key to search for
- `session_id: str`: If provided, only `Memory` objects with a matching session ID will be considered
- `scope: MemoryScope`: If provided, only memory objects with a matching scope will be considered (otherwise all objects will be considered)

Returns:
- `Tuple[bool, Any]`: A flag indicating whether the key/value pair was found, and the corresponding value; this can be unpacked as shown below

```python
found, value = getMemoryValue(memories, "key", "session_id")
```

### Common session memory values

We have defined two memory objects which can be used to share information in a common format between skills:

```python
class UserIdentity(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    preferredName: Optional[str] = None
    id: Optional[str] = None

class UserLocation(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
```

Users may define their own objects to work across their skills, or to expose information to other skills. These values can be set and retrieved from a memory array using the following helper functions:

- `set_user_identity(memories: List[Memory], *, first_name: Optional[str] = None, last_name: Optional[str] = None, preferred_name: Optional[str] = None, id: Optional[str] = None) -> None`
- `get_user_identity(memories: List[Memory]) -> Optional[UserIdentity]`
- `set_user_location(memories: List[Memory], *, city: Optional[str] = None, country: Optional[str] = None) -> None`
- `get_user_location(memories: List[Memory]) -> Optional[UserLocation]`

The classes and helper functions can be accessed from the `smskillsdk.utils.memory_values` namespace.
