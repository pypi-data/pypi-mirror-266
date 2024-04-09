import os
from datetime import datetime
from dotenv import load_dotenv

from kiteconnect import KiteConnect

PROJECT_ROOT = os.path.abspath("")
load_dotenv(PROJECT_ROOT + "/.env")


KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_API_SECRET = os.getenv("KITE_API_SECRET")

if KITE_API_KEY == None or KITE_API_SECRET == None:
    raise ValueError(
        "KITE API key or secret not found in .env file. Please set them.")


access_token_file = f"zerodha_access_token_{datetime.now().date()}.txt"


def login():
    kite = KiteConnect(api_key=KITE_API_KEY)

    if access_token_file not in os.listdir():
        print(">> Access Token is Missing")

        print('>> Let\'s first fetch "Request Token" by logging into the following url:')
        login_url = kite.login_url()
        print(login_url)

        request_token = input("Enter your fetched request token: ")

        print(">> Provided request token is taken into context")

        print(">> Generating the new Access Token...")

        access_token = kite.generate_session(
            request_token, KITE_API_SECRET)["access_token"]
        kite.set_access_token(access_token)

        with open(PROJECT_ROOT + f"/{access_token_file}", "w") as file:
            file.write(access_token)
            print(f">> Access Token is generated at: {access_token_file}")

    else:
        print(f">> You have already logged in for the day")

        access_token = None
        with open(PROJECT_ROOT + f"/{access_token_file}", "r+") as file:
            access_token = file.read(access_token)
        kite.set_access_token(access_token)

    return kite


kite = login()
