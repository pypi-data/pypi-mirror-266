from atcommon.models.base import BaseCoreModel
from atcommon.tools import format_time_ago
from atcommon.models.bi import BIAnswer

class ChatCore(BaseCoreModel):
    __properties_init__ = ['tenant_id', 'id', 'datasource_ids', 'human_msgs', 'ai_msgs', 'created', 'latest_msg']

    def __repr__(self):
        return f"<Chat {self.id} [{format_time_ago(self.created)}]>"


class MessageCore(BaseCoreModel):

    # role: human | ai
    __properties_init__ = ['id', 'chat_id', 'created', 'role', 'content', 'reply_to_msg_id']

    def __repr__(self):
        if self.role == 'ai':
            return f"[{self.id}] [{self.role}] {BIAnswer.load_from_dict(self.content)} [{format_time_ago(self.created)}]>"
        else:
            return f"[{self.id}] [{self.role}] {self.content} [{format_time_ago(self.created)}]>"


class RunCore(BaseCoreModel):
    # status: running | finished | failed | canceled
    __properties_init__ = ['id', 'chat_id', 'created', 'status', 'steps']

    def __repr__(self):
        return f"<ChatRun {self.id} [{format_time_ago(self.created)}]>"
