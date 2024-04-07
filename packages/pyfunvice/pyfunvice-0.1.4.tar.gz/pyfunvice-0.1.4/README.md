# Pyfunvice is FaaS SDK for Python

If you want to write an HTTP service based on python, your service is very simple, and at the same time you don’t want to add a complicated HTTP framework, Pyfunvice will be your best choice.

First, you need to install pyfunvice

```bash
pip install pyfunvice
```

And a very simple example will be provided below

```python
from pyfunvice import faas, faas_with_dict_req, start_faas

@faas(path="/api/v1/greet")
async def v1_greet(data: dict) -> dict:
    name = data["name"]
    age = data["age"]
    return {"name": name, "age": age, "status": "success"}

if __name__ == "__main__":
    start_faas()
```

That's all, a HTTP service will be run and the default port is 8000 and the path is /api/v1/greet

If you want to change the default port, you can add port parameter

```python
from pyfunvice import faas, faas_with_dict_req, start_faas

@faas(path="/api/v1/greet")
async def v1_greet(data: dict) -> dict:
    name = data["name"]
    age = data["age"]
    return {"name": name, "age": age, "status": "success"}

if __name__ == "__main__":
    start_faas(port=8080)
```

And if you want to increase the number of workers, you can add workers parameter, it will run n worker processes in parallel

```python
from pyfunvice import faas, faas_with_dict_req, start_faas

@faas(path="/api/v1/greet")
async def v1_greet(data: dict) -> dict:
    name = data["name"]
    age = data["age"]
    return {"name": name, "age": age, "status": "success"}

if __name__ == "__main__":
    start_faas(port=8080, workers=2)
```