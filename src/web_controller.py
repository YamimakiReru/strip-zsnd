import r_framework as r

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn
import threading
import webbrowser
import time

class WebStripZsndController:
    _HOSTNAME = '127.0.0.1'

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
        self._fast_api.get('/')(self.index)
        self._fast_api.mount('/', StaticFiles(directory=('resources')))

    def index(self):
        return RedirectResponse('/index.html')
