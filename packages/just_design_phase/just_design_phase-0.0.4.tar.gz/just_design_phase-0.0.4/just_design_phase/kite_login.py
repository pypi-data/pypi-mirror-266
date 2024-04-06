import os

from kiteconnect import KiteConnect

PROJECT_ROOT = os.path.dirname(os.path.abspath(""))

KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_API_SECRET = os.getenv("KITE_API_SECRET")


def login():
    kite = KiteConnect(api_key=KITE_API_KEY)
    with open(PROJECT_ROOT + "/sample.txt", "r+") as file:
        file.write("Hello World")


kite = login()
