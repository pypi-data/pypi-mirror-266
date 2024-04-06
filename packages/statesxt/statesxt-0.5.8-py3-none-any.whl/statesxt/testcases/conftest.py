import pytest

# from database.service import DBService
from base.base_driver import BaseDriver
from ._fixtures.composition import *
from ._fixtures.auth import *
from ._fixtures.option import *
from ._fixtures.param import *


@pytest.fixture(scope="class")
def setup(request, logger, browser, domain, service_account, store):
    logger

    # setup driver
    base = BaseDriver(browser, domain, fullscreen=True)

    # setup service
    # service = DBService(domain)
    # service.start()

    # set requests
    request.cls.base = base
    request.cls.sa = service_account
    request.cls.store = store
    # request.cls.service = service

    yield

    # service.end()
    base.exit()
