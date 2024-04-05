"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
===
http://www.apache.org/licenses/LICENSE-2.0
https://stackoverflow.com/questions/53039551/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detec
https://github.com/diprajpatra/selenium-stealth
"""
import traceback
import time
import uuid
from multiprocessing.connection import Listener
from queue import Queue
from itertools import count
from threading import Thread
from web_render.tool import log

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Union, Any
from web_render.flask.core.service.interface import MessageProtocol
from dataclasses import dataclass
from web_render.base.abstract import SeleniumRender

logger = log(__name__)

@dataclass
class IRender:
    id: str = None
    html: str = None
    url: str = None
    expiration_date: Any = None
    javascript: Any = None
    web_wait: Any = None


class ServerRender:
    data: Dict = dict()
    queue = Queue()
    timeout_clear = 60

    def __init__(self, render: Union[SeleniumRender]):
        self._render = render

    def set_url(self, message: MessageProtocol):
        payload = IRender(**message.payload)
        self._render.set_url(payload.url, web_wait=payload.web_wait)
        if payload.javascript:
            self._render.browser.execute_script(payload.javascript)

        # web wait
        # for wait in payload.selector_wait:
        # self._render.browser.web_until

        ServerRender.data[payload.id] = {
            "id": payload.id,
            "html" : self._render.get_content(),
            "expiration_date": payload.expiration_date,
        }


    def get_content(self, message: MessageProtocol)-> Union[Dict, None]:
        render_data = ServerRender.data.get(message.payload['id'])
        if render_data:
            return render_data

    def get_live_content(self, message: MessageProtocol) -> Dict:
        payload = IRender(**message.payload)
        if payload.javascript:
            self._render.browser.execute_script(payload.javascript)
        return {
            "html": self._render.get_content(),
        }

    def work_service(self):
        for _ in count():
            message = self.queue.get()
            try:
                self.set_url(message)
            except Exception as e:
                logger.error(f"Error {e}", exc_info=True)

    def clear_service(self):
        for _ in count():
            for k in list(ServerRender.data.keys()):
                if ServerRender.data[k]['expiration_date'] < datetime.now().timestamp():
                    ServerRender.data.pop(k)
            time.sleep(self.timeout_clear)

    def client_service(self, conn):
        try:
            while True:
                payload = conn.recv()
                message = MessageProtocol(**payload)

                logger.debug(f"controller. incoming message {message}")
                if message.action == "open_page":
                    task_id = uuid.uuid4().hex
                    message.payload['id'] = task_id
                    self.queue.put(message)
                    conn.send(task_id)

                if message.action == "content":
                    conn.send(self.get_content(message))

                if message.action == "live_content":
                    data = self.get_live_content(message)
                    conn.send(data)
                # conn.send( payload )
        except EOFError:
            logger.debug(f"Connect closed {conn}")

    def server(self, address, authkey):
        serv = Listener(address, authkey=authkey)
        with ThreadPoolExecutor(max_workers=4) as executor:
            for _ in count():
                try:
                    client = serv.accept()
                    executor.submit(self.client_service, client)
                except Exception:
                    traceback.print_exc()

    def run(self, address, authkey):
        try:
            Thread(target=self.work_service, daemon=True).start()
            Thread(target=self.clear_service, daemon=True).start()
            logger.info(f"Server run: {address}")
            self.server(address, authkey=authkey)
        finally:
            self._render.quit()
            logger.info("Drop process")
