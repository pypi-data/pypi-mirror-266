# 通用的数据源类，提供了各种数据源均需要的基本属性和方法，比如Original MetaData以及获取MetaData的方法
from atcommon.models.base import BaseCoreModel


class DataSourceCore(BaseCoreModel):

    __properties_init__ = ['tenant_id', 'id', 'created_at',
                           'name', 'type', 'access_config',
                           'sample_questions', 'meta_status']

    def __repr__(self):
        if self.id:
            return f"<{self.id}>"
        else:
            return f"<{self.type} (not saved)>"

    def __str__(self):
        return self.__repr__()

    @property
    def safe_access_config(self):
        # 复制access_config以避免修改原始数据
        safe_config = dict(self.access_config)
        # 定义需要替换值的敏感键列表
        sensitive_keys = ['password', 'pwd', 'passwd']

        # 遍历敏感键列表，将敏感信息值替换为"******"
        for key in sensitive_keys:
            if key in safe_config:
                safe_config[key] = "******"
        return safe_config

    def safe_to_dict(self):
        # 首先调用基类的 to_dict 方法获取字典表示
        data = super().to_dict()

        # 然后获取安全的 access_config
        safe_access_config = self.safe_access_config

        # 替换 access_config 为其安全版本
        data['access_config'] = safe_access_config

        return data
