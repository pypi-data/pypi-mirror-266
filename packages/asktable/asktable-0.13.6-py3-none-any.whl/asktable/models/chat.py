from datetime import datetime
from atcommon.models import ChatCore
from atcommon.tools import format_time_ago
from asktable.models.base import convert_to_object, BaseResourceList
from asktable.models.run import RunList
from asktable.models.message import MessageList, MessageClientModel


class ChatClientModel(ChatCore):


    def delete(self):
        return self.api.send(endpoint=f"/chats/{self.id}", method="DELETE")

    @property
    def runs(self):
        return RunList(self.api, endpoint=f"/chats/{self.id}/runs")

    @property
    def messages(self):
        return MessageList(self.api, endpoint=f"/chats/{self.id}/messages")

    @convert_to_object(cls=MessageClientModel)
    def ask(self, question):
        # 提问
        data = {"question": question}
        return self.api.send(endpoint=f"/chats/{self.id}", method="POST",
                             data=data)


class ChatList(BaseResourceList):
    __do_not_print_properties__ = ['tenant_id']

    def _my_format_time(self, ts: int or None):
        if not ts:
            return ''
        local_ts_readable = format_time_ago(ts)
        return local_ts_readable

    @convert_to_object(cls=ChatClientModel)
    def _get_all_resources(self):
        return self._get_all_resources_request()

    def _get_all_resources_request(self):
        # 获取资源
        params = {
            "order": self.order,
            "page_number": self.page_number,
            "page_size": self.page_size
        }
        response = self.api.send(endpoint=self.endpoint, method="GET", params=params)

        chats = response.get('data', [])

        # 转换 created 字段
        for chat in chats:
            chat['created'] = self._my_format_time(chat['created'])
            chat['latest_msg'] = self._my_format_time(chat['latest_msg'])
        return chats

    @property
    @convert_to_object(cls=ChatClientModel)
    def latest(self):
        # 获取最后一个资源
        return self._get_all_resources_request()[0]

    def page(self, page_number=1):
        return ChatList(self.api, self.endpoint, page_number=page_number)

    def all(self):
        return ChatList(self.api, self.endpoint, page_number=0, page_size=0)

    @convert_to_object(cls=ChatClientModel)
    def get(self, id):
        # 通过资源ID来获取
        return self.api.send(endpoint=f"{self.endpoint}/{id}", method="GET")

    @convert_to_object(cls=ChatClientModel)
    def create(self, datasource_ids: list[str]):
        for ds_id in datasource_ids:
            if type(ds_id) != str:
                raise ValueError(f"datasource_ids must be a list of string: {ds_id}")

        data = {"datasource_ids": datasource_ids}
        return self.api.send(endpoint=self.endpoint, method="POST", data=data)
