import os
from datetime import datetime
from dotenv import find_dotenv, load_dotenv

from kiteconnect import KiteConnect

find_dotenv(load_dotenv())

PROJECT_ROOT = os.path.abspath("")

KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_API_SECRET = os.getenv("KITE_API_SECRET")

access_token_file = f"zerodha_access_token_{
    datetime.now().date()}.txt"


def login():
    kite = KiteConnect(api_key=KITE_API_KEY)

    if access_token_file not in os.listdir():
        print("Fetch request token by logging into the following url: \n")
        login_url = kite.login_url()
        print(login_url)
        request_token = input("Enter your fetched request token: ")

        access_token = kite.generate_session(
            request_token, KITE_API_SECRET)["access_token"]
        kite.set_access_token(access_token)

        with open(PROJECT_ROOT + f"/{access_token_file}", "w") as file:
            file.write(access_token)

    else:
        print("You have already logged in for today")
        access_token = None
        with open(PROJECT_ROOT + f"/{access_token_file}", "r+") as file:
            access_token = file.read(access_token)
        kite.set_access_token(access_token)

    return kite


# kite = login()

print(os.getenv("KITE_API_KEY"))
