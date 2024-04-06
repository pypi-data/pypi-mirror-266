
from atcommon.models import MessageCore, BIAnswer
from atcommon.tools import format_time_ago
from asktable.models.base import convert_to_object, BaseResourceList


class MessageClientModel(MessageCore):

    @property
    def answer(self):
        if self.role == 'ai':
            return BIAnswer.load_from_dict(self.content)
        else:
            return None



class MessageList(BaseResourceList):
    __do_not_print_properties__ = ['chat_id']

    @convert_to_object(cls=MessageClientModel)
    def _get_all_resources(self):
        # 获取所有资源
        msgs = self.api.send(endpoint=self.endpoint, method="GET")
        for m in msgs:
            m['created'] = format_time_ago(m['created'])
            if m['role'] == 'ai':
                answer = BIAnswer.load_from_dict(m['content'])
                m['content'] = answer
        return msgs

    @convert_to_object(cls=MessageClientModel)
    def get(self, id):
        # 通过ID来获取
        return self.api.send(endpoint=f"{self.endpoint}/{id}", method="GET")

    @convert_to_object(cls=MessageClientModel)
    def create(self, content):
        # 发送消息
        data = {"content": content}
        return self.api.send(endpoint=f"{self.endpoint}", method="POST", data=data)

