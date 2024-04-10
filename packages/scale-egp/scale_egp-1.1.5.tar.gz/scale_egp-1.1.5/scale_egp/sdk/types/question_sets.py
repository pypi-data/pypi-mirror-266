from __future__ import annotations

from typing import List, Optional


from scale_egp.utils.model_utils import Entity, BaseModel
from scale_egp.sdk.types.questions import Question


class QuestionSet(Entity):
    """
    A data model representing a question set.

    Attributes:
        id: The ID of the question set
        name: The name of the question set
        created_at: The time the question set was created
        created_by_user_id: The user ID of the user who created the question set
        account_id: The account ID of the account that the question set is associated with
        questions: The questions in the question set
    """

    id: str
    name: str
    created_at: str
    created_by_user_id: str
    account_id: str
    questions: Optional[List[Question]]


class QuestionSetRequest(BaseModel):
    name: str
    account_id: str
    question_ids: List[str]

