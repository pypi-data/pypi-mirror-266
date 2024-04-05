"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
from multiprocessing.connection import Client
from web_render.interface import MessageProtocol
from datetime import datetime, timedelta


class BrowserClient:
    def __init__(self, address, authkey):
        self.address = address
        self.authkey = authkey

    def send_command(self, command):
        with Client(self.address, authkey=self.authkey) as conn:
            conn.send(command)
            response = conn.recv()
        return response


def open_page(form: dict, address, auth_key):
    client = BrowserClient(address, auth_key)
    form.update({
        'expiration_date': int((datetime.now() + timedelta(seconds=60*5)).timestamp())
    })
    message = MessageProtocol(
        action='open_page',
        payload=form)
    result = client.send_command(message.to_dict())
    return result


def get_content(task_id, address, auth_key):
    client = BrowserClient(address, auth_key)
    message = MessageProtocol(action='content', payload={'id': task_id})
    result = client.send_command(message.to_dict())
    return result


def get_live_content(data, address, auth_key):
    client = BrowserClient(address, auth_key)
    message = MessageProtocol(payload=data, action='live_content')
    result = client.send_command(message.to_dict())
    return result
