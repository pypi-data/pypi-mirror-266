from __future__ import annotations

from typing import Dict, Optional, Union, List, Literal

from pydantic import Field

from scale_egp.utils.model_utils import Entity, BaseModel, RootEntity
from scale_egp.sdk.enums import QuestionType

class CategoricalChoice(BaseModel):
    """
    A choice for a categorical question.

    This is only used in `HUMAN` evaluation type to specify a choice for a  question
    that will be asked to users when they are evaluating generated outputs in the SGP annotation UI.

    Attributes:
        label: The text displayed to annotators for this choice.
        value: The value reported in the TestCaseResult for this question if this choice is
            selected.

            If users would like to track the improvement of a model over time, it is
            recommended to use a numeric value for this field.

            A string value can be used if no ordering is desired.
        audit_required: Whether selecting this choice will flag the test case result. Defaulted to false.
    """

    label: str
    value: Union[str, int, bool]
    audit_required: bool = Field(default=False)
    
    def to_dict(self):
        return {
            "label": self.label,
            "value": self.value,
            "audit_required": self.audit_required,
        }

# TODO <cathy-scale>: Turn Union[str, List[str]] into a CategoricalRule type when supporting more complex rules
CategoricalCondition = Dict[str, Union[str, List[str]]]
"""
A mapping from `question_id` to either the exact value that must be selected, or a list of
acceptable values. All key-value pairs in the mapping must be satisfied for the condition to be `True`.
For questions with `multi=True`, the selected values include at least one of the acceptable values.
"""

class BaseQuestion(Entity):
    """
    A base class for questions.

    Attributes:
        id: A unique id for this question. Each question_id will be represented as a
            key in the `result` field in the TestCaseResult after an annotation is completed.
            When examining how an application has performed on a specific question, users should
            look at the `result` field in the TestCaseResult for the key with the
            corresponding id.
        title: The text displayed to annotators for this question.
        prompt: The prompt displayed to annotators for this question.
        required: Whether this question is required. If
            `True`, the annotator must select at least one choice.
        conditions: Conditions that allow the question to be rendered.
            Example 1: `conditions=[{"accurate": "very", "complete": "yes"}]` means that the selected
            value for `accurate` must be `"very"` and the selected value for `complete` must be
            `"yes"`. Example 2: `conditions=[{"accurate": ["mostly", "very"]}, {"complete": "yes"}]`
            means that either the selected value for `accurate` must be `"mostly"` or `"very"`,
            or the selected value for `complete` must be `"yes"`.
        account_id: The account ID of the account that the question is associated with.
        created_at: The time the question was created.
        created_by_user_id: The user ID of the user who created the question.
    """
    id: str
    title: str
    prompt: str
    required: bool = Field(default=False)
    conditions: Optional[List[CategoricalCondition]]
    account_id: str
    created_at: str
    created_by_user_id: str


class CategoricalQuestion(BaseQuestion):
    """
    A categorical question.

    This is only used in `HUMAN` evaluation type to specify a choice for a  question
    that will be asked to users when they are evaluating generated outputs in the SGP annotation UI.

    Attributes:
        type: The type of the question.
        choices: The choices for the question.
        multi: Whether to allow multiple choices to be selected. If `True`, displays as a
            checkbox list. Otherwise, displays as a radio group.
        dropdown: Whether to display options as a dropdown list. If `True`, displays as a
            dropdown. Otherwise, displays as a radio group. Currently, dropdown cannot be true
            if multi is true.
    """

    type: Literal[QuestionType.CATEGORICAL] = QuestionType.CATEGORICAL.value
    choices: List[CategoricalChoice]
    multi: bool = Field(default=False)
    dropdown: Optional[bool] = Field(default=False)


class FreeTextQuestion(BaseQuestion):
    """
    A free text question.

    This is only used in `HUMAN` evaluation type to specify a choice for a  question
    that will be asked to users when they are evaluating generated outputs in the SGP annotation UI.

    Attributes:
        type: The type of the question.
    """

    type: Literal[QuestionType.FREE_TEXT] = QuestionType.FREE_TEXT.value


class Question(RootEntity):
    __root__: Union[CategoricalQuestion, FreeTextQuestion] = Field(
        ...,
        discriminator="type",
    )


class QuestionRequest(BaseModel):
    type: str
    title: str
    prompt: str
    account_id: str
    choices: Optional[List[dict]]
    multi: Optional[bool]
    dropdown: Optional[bool]
    required: Optional[bool]
    conditions: Optional[List[dict]]
