from seleniumwire.utils import decode
from seleniumwire import webdriver
import json


class ResponseHandler:
    """To get response of calls (making use selenium-wire)"""

    def get_response(self, driver: webdriver, prefix=""):
        data = []
        for request in driver.requests:
            if request.response:
                if request.url.startswith(prefix):
                    response = request.response
                    body = decode(
                        response.body,
                        response.headers.get("Content-Encoding", "identity"),
                    )
                    decoded_body = body.decode("utf-8")
                    json_data = json.loads(decoded_body)
                    data.append(json_data)
        return data
