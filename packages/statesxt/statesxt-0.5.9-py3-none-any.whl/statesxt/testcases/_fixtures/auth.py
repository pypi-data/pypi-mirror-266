import logging
import pytest
import json
import sys

from testcases.top_menu.page import TopMenuPage
from testcases.login.page import LoginPage


accounts = json.load(open("./database/mocks/mock_login_valid.json"))


@pytest.fixture(scope="function")
def auth(request):
    try:
        LoginPage(request.cls.base).login(
            accounts[request.cls.role]["username"],
            accounts[request.cls.role]["password"],
        )
        yield
        TopMenuPage(request.cls.base).logout()
    except Exception as e:
        logging.getLogger(f"root.{__name__}.{sys._getframe().f_code.co_name}").error(f"login error:\n{str(e)}")
        raise Exception(str(e))
