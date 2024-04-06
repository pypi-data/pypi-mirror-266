import pytest

"""
Set Role
"""
# region


@pytest.fixture(scope="class")
def admin(request):
    request.cls.role = "admin"


@pytest.fixture(scope="class")
def manager(request):
    request.cls.role = "manager"


@pytest.fixture(scope="class")
def operator(request):
    request.cls.role = "operator"


@pytest.fixture(scope="class")
def supervisor(request):
    request.cls.role = "supervisor"


# endregion


"""
Set Use Case
"""


# region
@pytest.fixture(scope="class")
def usecase1(request):
    request.cls.usecase = 1


@pytest.fixture(scope="class")
def usecase2(request):
    request.cls.usecase = 2


@pytest.fixture(scope="class")
def usecase3(request):
    request.cls.usecase = 3


@pytest.fixture(scope="class")
def usecase4(request):
    request.cls.usecase = 4


@pytest.fixture(scope="class")
def usecase5(request):
    request.cls.usecase = 5


@pytest.fixture(scope="class")
def usecase6(request):
    request.cls.usecase = 6


@pytest.fixture(scope="class")
def usecase7(request):
    request.cls.usecase = 7


# endregion
