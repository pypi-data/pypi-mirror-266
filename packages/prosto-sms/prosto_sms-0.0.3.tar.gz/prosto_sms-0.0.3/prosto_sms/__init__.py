from typing import Optional

import requests
from loguru import logger

from . import exceptions
from . import methods


class API:
    """
    Main api class
    """

    def __init__(
        self,
        email: str = None,
        password: str = None,
        key: str = None
    ):
        """
        Initializing the API

        :param email: account email address
        :param password: account password
        :param key: api key
        """

        self.email = email
        self.password = password
        self.key = key
        self.api_url = "https://ssl.bs00.ru"
        self.methods = methods.Methods(self)

    def request(self, method: str, data: dict = None) -> Optional[dict]:
        """
        Method for requesting information

        :param method: required method
        :param data: request parameters
        :return: response data
        """

        if data is None:
            data = {}

        data["format"] = "json"
        if not data.get("method"):
            data["method"] = method

        if self.key and not (self.email and self.password):
            data["key"] = self.key
        elif (self.email and self.password) and not self.key:
            data["email"] = self.email
            data["password"] = self.password
        else:
            raise exceptions.NoAuthData(
                "email and password OR key is required"
            )

        try:
            result = requests.get(
                url=self.api_url,
                params=data,
                timeout=30
            )
            result.raise_for_status()

            result = result.json()
        except Exception as err:
            logger.exception(err)
            return

        if result["response"]["msg"].get("type") == "error":
            raise exceptions.RequestError(
                result["response"]["msg"]["text"]
            )

        return result["response"]["data"]
