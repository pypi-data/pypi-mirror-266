import os

from .constants import PLATFORM_API_KEY_NAME, CREDENTIALS_AUTH_METHOD_API_KEY_KEY
from .exceptions import CredentialAPIKeyMissingException


class Credentials:
    # TODO[VIMPORTANT] CHECK AND MAKE FUNCTIONS PRIVATE IF THEY SHOULD NOT BE ACCESSIBLE DIRECTLY

    method = CREDENTIALS_AUTH_METHOD_API_KEY_KEY
    api_key = None

    def __init__(self, *, api_key=None) -> None:

        if api_key == None:
            api_key = os.environ.get(PLATFORM_API_KEY_NAME, None)

        if api_key == None:
            raise CredentialAPIKeyMissingException()

        self.api_key = api_key
