from dataclasses import dataclass, field
import datetime
import random
from typing import List, Optional
import time
import uuid

from dataclasses_json import DataClassJsonMixin
from danoan.toml_dataclass import TomlDataClassIO

@dataclass
class CfgDcNtfy(TomlDataClassIO):
    url: str = field(default="https://ntfy.sh/app")
    topic: str = field(default="test")
    token: str = field(default="")
@dataclass
class Attachment:
    name: str
    type: str
    size: int
    expires: int
    url: str
def _rand_id():
    return str(uuid.uuid4())
def _nt():
    return int(datetime.datetime.now().timestamp)
@dataclass
class RecvNtfyMessage(DataClassJsonMixin):
    message: str
    id: str = field(default_factory=_rand_id)
    time: int = field(default_factory=_nt)
    expires: Optional[int] = field(default=None)
    event: str = field(default="message")
    topic: str = field(default="")
    priority: int = field(default=1) # 1,2,3,4,5
    tags: List[str] = field(default_factory=list)
    click: Optional[str] = field(default=None)
    attachment: Optional[Attachment] = field(default=None)
    title: str = field(default="")
@dataclass
class Action(DataClassJsonMixin):
    action: str
    label: str
    url: str


@dataclass
class SendNtfyMessage(DataClassJsonMixin):
    message: str
    topic: str= field(default="")
    title: str= field(default="")
    tags: List[str]= field(default_factory=list)
    priority: int = field(default=1) # 1,2,3,4,5
    attach: Optional[str] = field(default=None)
    filename: Optional[str] = field(default=None)
    click: Optional[str] = field(default=None)
    actions: List[Action] = field(default_factory=list)
