import pytest
import softest

from ..page import ExamplePage


@pytest.mark.order(1)
@pytest.mark.usefixtures("setup")
class TestExample(softest.TestCase):
    """Test cases for Example page"""

    @pytest.fixture(autouse=True)
    def class_setup(self, auth, request):
        self.p = ExamplePage(self.base, request.cls.usecase)
