"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
from dataclasses import dataclass, field, asdict
from typing import List, Any, Union, Dict


@dataclass
class MessageProtocol:
    status_code: int = 200
    payload: Union[List, Dict, None] = None
    action: str = str()
    message: str = str()

    def to_dict(self):
        return asdict(self)