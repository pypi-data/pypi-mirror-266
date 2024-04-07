from fastapi.params import Form
from gunicorn.app.base import BaseApplication
from fastapi import APIRouter, FastAPI, File, Request, UploadFile
from functools import wraps
import inspect
import subprocess
import aiofiles

from pyfunvice.common_func import delete_file, get_uuid
from pyfunvice.struct import ResponseModel

app = FastAPI()
faas_router = APIRouter()


def faas(path="/", body_type="raw", inparam_type="dict"):
    """
    path : str = "/",                       # http path
    body_type : str = "raw", "form-data"    # http body type
    inparam_type : str = "dict", "flat"     # faas inparam type
    """

    def decorator(func):
        if body_type == "raw":
            if inparam_type == "dict":

                @wraps(func)
                async def wrapper(data: dict):
                    return await func(data)

                @faas_router.post(path)
                async def process_function(request: Request):
                    try:
                        data = await request.json()
                        result = await wrapper(data)
                        return ResponseModel(
                            requestId=data.get("requestId"),
                            code="200",
                            message="success",
                            data=result,
                        )
                    except Exception as e:
                        return ResponseModel(
                            requestId=data.get("requestId"),
                            code="500",
                            message=str(e),
                            data={},
                        )

                return func
            elif inparam_type == "flat":

                @wraps(func)
                async def wrapper(*args, **kwargs):
                    return await func(*args, **kwargs)

                signature = inspect.signature(func)
                parameters = list(signature.parameters.values())

                @faas_router.post(path)
                async def process_function(request: Request):
                    try:
                        data = await request.json()
                        args = [data.get(param.name) for param in parameters]
                        result = await wrapper(*args)
                        return ResponseModel(
                            requestId=data.get("requestId"),
                            code="200",
                            message="success",
                            data=result,
                        )
                    except Exception as e:
                        return ResponseModel(
                            requestId=data.get("requestId"),
                            code="500",
                            message=str(e),
                            data={},
                        )
            else:
                pass
        elif body_type == "form-data":

            @wraps(func)
            async def wrapper(file_name: str, file: UploadFile = File(...)):
                async with aiofiles.open(file_name, "wb") as out_file:
                    content = await file.read()
                    await out_file.write(content)
                result = await func(file_name)
                delete_file(file_name)
                return result

            @faas_router.post(path)
            async def process_function(
                file: UploadFile = File(...),
                requestId: str = Form(None),
            ):
                try:
                    if not file:
                        raise Exception("file is empty")
                    if requestId is None or len(requestId) == 0:
                        requestId = get_uuid()
                    file_name: str = requestId
                    result = await wrapper(file_name, file)
                    return ResponseModel(
                        requestId=requestId,
                        code="200",
                        message="success",
                        data=result,
                    )
                except Exception as e:
                    return ResponseModel(
                        requestId=requestId,
                        code="500",
                        message=str(e),
                        data={},
                    )
        else:
            pass
        return func

    return decorator


class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def start_faas(port: int = 8000, workers: int = 1):
    app.include_router(faas_router)
    options = {
        "bind": f"0.0.0.0:{port}",
        "timeout": 7200,
        "workers": workers,
        "worker_class": "uvicorn.workers.UvicornWorker",
    }
    StandaloneApplication(app, options).run()


def start_fass_with_cmd(port: int = 8000, workers: int = 1):
    gunicorn_cmd = (
        f"poetry run gunicorn "
        "pyfunvice:app "
        f"--timeout 7200 "
        f"--workers {workers} "
        "--worker-class uvicorn.workers.UvicornWorker "
        f"--bind 0.0.0.0:{port}"
    )
    result = subprocess.run(gunicorn_cmd, shell=True, check=True, text=True)
    print(result)
