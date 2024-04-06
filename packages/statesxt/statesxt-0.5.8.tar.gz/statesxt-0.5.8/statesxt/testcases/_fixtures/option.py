import pytest


def pytest_addoption(parser):
    parser.addoption("--browser", "-B")
    parser.addoption("--domain", "-D")
    parser.addoption("--report")
    parser.addoption("--tfo")
    parser.addoption("--use_email")
    parser.addoption(
        "--number-help",
        action="store_true",
        default=False,
        help="Print custom number help information and exit.",
    )


@pytest.fixture(scope="session")
def browser(request):
    req = request.config.getoption("--browser") or request.config.getoption("-B")
    return req if req else "edge"


@pytest.fixture(scope="session")
def domain(request):
    req = request.config.getoption("--domain") or request.config.getoption("-D")
    return req if req else None


@pytest.fixture(scope="session")
def report(request):
    req = request.config.getoption("--report")
    return req if req else "0"


@pytest.fixture(scope="session")
def tfo(request):
    req = request.config.getoption("--tfo")
    return req if req else "1"


@pytest.fixture(scope="session")
def use_email(request):
    req = request.config.getoption("--use_email")
    return req if req else "0"


def pytest_collection_modifyitems(config, items):
    if config.option.number_help:
        print(
            """
        Browser:
        - 1 = brave
        - 2 = chrome
        - 3 = edge
        - 4 = firefox

        Domain:
        - None
        """
        )
        items.clear()
