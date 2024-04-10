__title__ = 'ZAmino.fix'
__author__ = 'ZOOM'
__copyright__ = 'Copyright (c) 2024 ZOOM37Z'
__version__ = '1.1.2'




from .acm import ACM
from .client import Client
from .sub_client import SubClient
from .lib.util import exceptions, helpers, objects, headers
from .asyncfix import acm, client, sub_client, socket
from .socket import Callbacks, SocketHandler
from requests import get
from json import loads

__newest__ = loads(get("https://pypi.org/pypi/amino.fix/json").text)["info"]["version"]



if __version__ != __newest__:
    print(f"New version of {__title__} available: {__newest__} (Using {__version__})")
    print("Visit our Telegram - https://t.me/ZAminoZ")