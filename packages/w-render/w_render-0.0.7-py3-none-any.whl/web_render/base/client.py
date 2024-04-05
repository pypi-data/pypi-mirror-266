"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
from multiprocessing.connection import Client
from datetime import datetime, timedelta
from web_render.interface import MessageProtocol

class BrowserClient:
    def __init__(self, address, authkey):
        self.address = address
        self.authkey = authkey

    def send_command(self, command):
        with Client(self.address, authkey=self.authkey) as conn:
            print(conn)
            conn.send(command)
            response = conn.recv()
        return response

if __name__ == '__main__':
    client = BrowserClient(('localhost', 21000), b'qwerty')
    message = MessageProtocol(
        action='open_page',
        payload={
        'url': 'https://google.com',
        'expiration_date': int((datetime.now() + timedelta(seconds=60*5)).timestamp())
    })
    print(client.send_command(message.to_dict()))

    # message = MessageProtocol(action='live_content', payload={})
    # print(client.send_command(message.to_dict()))

    # breakpoint()
    # print(client.send_command({'action': 'content', 'page_id': 1}))