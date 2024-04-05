from typing import List

from pydantic import Field

from .base_model import BaseModel
from .fragments import NotificationRuleDetails


class GetNotificationRules(BaseModel):
    notification_rules: List["GetNotificationRulesNotificationRules"] = Field(
        alias="notificationRules"
    )


class GetNotificationRulesNotificationRules(NotificationRuleDetails):
    pass


GetNotificationRules.model_rebuild()
GetNotificationRulesNotificationRules.model_rebuild()
