from __future__ import annotations
from datetime import datetime

from scale_egp.sdk.enums import EvaluationType
from scale_egp.utils.model_utils import BaseModel, Entity

class EvaluationConfig(Entity):
    """
    A data model representing an evaluation config.

    Attributes:
        id: The ID of the evaluation config
        evaluation_type: The type of evaluation. Currently, only `HUMAN` is supported.
        question_set_id: The ID of the question set to use for the evaluation.
        account_id: The account ID of the account that the evaluation config is associated with.
        created_at: The time the evaluation config was created.
        created_by_user_id: The user ID of the user who created the evaluation config.
    """

    id: str
    evaluation_type: EvaluationType
    question_set_id: str
    account_id: str
    created_at: datetime
    created_by_user_id: str


class EvaluationConfigRequest(BaseModel):
    evaluation_type: EvaluationType
    question_set_id: str
    account_id: str
