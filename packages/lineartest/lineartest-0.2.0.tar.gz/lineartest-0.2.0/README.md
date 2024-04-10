# LinearTest
A testing framework working with Starlette TestClient.

- **Source code**: https://github.com/fanyf22/lineartest/
- **Documentation**: https://fanyf22.github.io/lineartest/

## Dependencies

```requirements
# requried
python>=3.10
starlette>=0.37.2
pydantic>=2.6.4

# recommended
httpx>=0.27.0   # for starlette.testclient
```

## Installing

The package is published on https://pypi.org/lineartest.

Use `pip` or `poetry` to install it.

```shell
# pip
pip install lineartest

# poetry
poetry add lineartest
```

Also, if you are using the `LinearClient` feature, which is based on `starlette.testclient.TestClient`, you may need to install `httpx`:

```shell
# pip
pip install httpx

# poetry
poetry add httpx
```

## Features

- `lineartest.schedule` helps you run tests one-by-one in order, and the tests run later can retrieve the results from the tests run earlier.
- `lineartest.client` helps you log the detail of a request and the response easily.

## Example

```python
from pydantic import BaseModel
from starlette.testclient import TestClient
from lineartest import LinearClient, schedule

# import your ASGI app here for testing
...

test_client = TestClient(app)
client = LinearClient(test_client)


# add `test_login` function to schedule
@schedule
def test_login(username, password):
    class Response(BaseModel):
        success: bool
        token: str

    # the parameters are the same as `TestClient`
    res = client.post('/login', data={
        'username': username,
        'password': password
    }, model=Response)  # use `model` parameter to specify a response model

    assert res.success
    return res.token    # the result will be stored by `schedule`

# add `test_resource` function to schedule
@schedule
def test_resource():
    # use `schedule.get` to retrieve history result
    token = schedule.get(test_login)

    class Response(BaseModel):
        success: bool

    res = client.get('/', headers={
        'Authorization': f'Bearer {token}'
    }, model=Response)

    assert res.success


# run the schedule
# you may pass positional or keyword arguments
schedule.run('username', password='password')
```

## License

This project is licensed under the terms of the MIT License.
