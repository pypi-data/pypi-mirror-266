from asktable.models import DataResourceList, ChatList
from asktable.api import APIRequest
from atcommon.version import VERSION


class AskTable:
    __version__ = VERSION
    version = VERSION

    def __init__(self, api_url='https://api.asktable.com',
                 token='token1', debug=False, user_id=None):
        self.api_url = api_url
        self.token = token
        self.debug = debug
        self.user_id = user_id

    @property
    def api(self):
        return APIRequest(api_url=self.api_url, token=self.token, debug=self.debug, user_id=self.user_id)

    @property
    def datasources(self):
        return DataResourceList(api=self.api, endpoint="/datasources")

    @property
    def chats(self):
        return ChatList(api=self.api, endpoint="/chats")

    @property
    def token_id(self):
        return self.api.send(endpoint="/account/token", method="GET")

