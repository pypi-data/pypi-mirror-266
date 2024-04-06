import os
import sys

from kiteconnect import KiteConnect

PROJECT_ROOT = os.path.dirname(sys.argv[0])

KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_API_SECRET = os.getenv("KITE_API_SECRET")


def login():
    kite = KiteConnect(api_key=KITE_API_KEY)
    with open(PROJECT_ROOT + "/sample.txt", "w") as file:
        file.write("Hello World")


kite = login()
