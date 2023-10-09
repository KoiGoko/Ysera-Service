from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List


def handle_cors(app: FastAPI, origins: List[str] = None):
    """
    Enable CORS (Cross-Origin Resource Sharing) for your FastAPI application.

    Parameters:
    - app (FastAPI): The FastAPI application instance.
    - origins (List[str]): A list of allowed origins. Defaults to ["*"].

    Example:
    ```python
    app = FastAPI()
    handle_cors(app, origins=["http://localhost", "http://localhost:3000"])
    ```

    Note: Make sure to add this middleware before defining your routes.
    """
    if origins is None:
        origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# 示例用法
app = FastAPI()
handle_cors(app, origins=["http://localhost", "http://localhost:3000"])
