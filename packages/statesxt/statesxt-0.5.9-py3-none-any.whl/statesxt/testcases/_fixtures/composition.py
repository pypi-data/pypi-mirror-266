import pytest
import os

from utils.email import Email
from utils.service_account import ServiceAccount
from utils.logger import Logger
from utils.store import Store


@pytest.fixture(scope="session")
def email(use_email):
    yield
    email = Email(
        sender_email=os.getenv("SENDER_EMAIL"),
        sender_password=os.getenv("SENDER_PASSWORD"),
        receiver_email=os.getenv("RECEIVER_EMAIL").split(","),
        receiver_name=os.getenv("RECEIVER_NAME").split(","),
    )
    if use_email == "1":
        try:
            print("\n\nSending email...")
            email.send()
            print("Email has been sent successfully")
        except Exception as e:
            print(f"Email failed to send: {str(e)}")


@pytest.fixture(scope="session")
def logger():
    lg = Logger()
    yield
    lg.shutdown()


@pytest.fixture(scope="session")
def service_account(report, tfo, domain):
    sa = ServiceAccount(
        spreadsheetName=os.getenv("SPREADSHEET_NAME"),
        folderId=os.getenv("FOLDER_ID"),
        domain=domain,
        testedFilesOnly=False if (tfo == "0") else True,
    )
    yield sa
    if report == "1":
        print("\n\nUpdating gsheet...")
        sa.update_all_values()
        sa.update_worksheet_colors()


@pytest.fixture(scope="session")
def store():
    store = Store()
    yield store
