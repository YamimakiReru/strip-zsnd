import r_framework as r

from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
import uvicorn
import http
from urllib.parse import urlsplit
import threading
import webbrowser
import time
from typing import Callable

_FN_DICT_KEY_ROUTE = '_zsnd_route'
_FN_DICT_KEY_METHOD = '_zsnd_method'

def _route(path: str, methods: list[str]) -> Callable[[Callable], Callable]:
    def decorator(func: Callable) -> Callable:
        func.__dict__[_FN_DICT_KEY_ROUTE] = path
        func.__dict__[_FN_DICT_KEY_METHOD] = methods
        return func
    return decorator

class WebStripZsndController:
    _HOSTNAME = '127.0.0.1'
    _VITE_URL = 'http://localhost:5173'

    @classmethod
    def serve(cls, port = 14514) -> int:
        '''
        :return: exit code
        '''
        threading.Thread(target=cls._open_browser, args=(port,)).start()
        factory = f'{WebStripZsndController.__module__}:{WebStripZsndController.__name__}.create_instance'
        uvicorn.run(factory, host=cls._HOSTNAME, port=port,
                reload=r.DEBUG, factory=True)
        # uvicorn.run() blocks here
        return 0

    @staticmethod
    def create_instance():
        fast_api = FastAPI()
        controller = WebStripZsndController(fast_api)
        controller._boot()
        return fast_api

    @classmethod
    def _open_browser(cls, port):
        time.sleep(1) # wait for the server to start
        webbrowser.open(f'http://{cls._HOSTNAME}:{port}/')

    def __init__(self, fast_api: FastAPI):
        self._fast_api = fast_api

    def _boot(self):
        self._register_route(self.index)
        self._register_route(self.frontend_proxy)

    def _register_route(self, func: Callable):
        assert _FN_DICT_KEY_ROUTE in func.__dict__, \
            f'@_route decorator not set on function {func.__name__}'
        path = func.__dict__[_FN_DICT_KEY_ROUTE]
        methods = func.__dict__[_FN_DICT_KEY_METHOD]
        self._fast_api.api_route(path, methods=methods)(func)

    @_route('/', ['GET'])
    async def index(self):
        return RedirectResponse('/index.html')

    @_route('/{path:path}', ['GET', 'POST'])
    async def frontend_proxy(self, request: Request, path: str):
        target = urlsplit(f"{self._VITE_URL}/{path}")
        conn = http.client.HTTPConnection(target.hostname, target.port)
        conn.request(
            request.method,
            target.path,
            body=await request.body(),
            headers=dict(request.headers)
        )
        res = conn.getresponse()
        body = res.read()
        return Response(body, res.status, dict(res.getheaders()))
