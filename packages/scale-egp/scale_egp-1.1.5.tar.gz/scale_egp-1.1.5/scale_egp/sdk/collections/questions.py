from typing import List, Optional


from scale_egp.sdk.types.questions import CategoricalChoice, Question, QuestionRequest
from scale_egp.utils.api_utils import (
    APIEngine,
)
from scale_egp.sdk.enums import QuestionType


class QuestionCollection(APIEngine):
    _sub_path = "v2/questions"

    def create(
        self,
        type: QuestionType,
        title: str,
        prompt: str,
        choices: Optional[List[CategoricalChoice]],
        multi: Optional[bool] = None,
        dropdown: Optional[bool] = False,
        required: Optional[bool] = False,
        conditions: Optional[List[dict]] = None,
        account_id: Optional[str] = None,
    ) -> Question:
        """
        Create a new Question.

        Args:
            type: The type of the Question.
            title: The title of the Question.
            prompt: The prompt of the Question.
            account_id: The ID of the account to create this Question for.
            choices: The choices of the Question.
            multi: Whether the question is multi-select
            dropdown: Whether the question is to be displayed as a dropdown
            required: Whether the question is required
            conditions: The conditions for the question
        Returns:
            The newly created Evaluation Configuration.
        """
        response = self._post(
            sub_path=self._sub_path,
            request=QuestionRequest(
                type=type.value,
                title=title,
                prompt=prompt,
                account_id=account_id or self._api_client.account_id,
                choices=[choice.to_dict() for choice in choices] if choices else None,
                multi=multi,
                dropdown=dropdown,
                required=required,
                conditions=conditions,
            ),
        )
        return Question.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> Question:
        """
        Get the details of a Question.

        Args:
            id: The ID of the Question.

        Returns:
            The Question.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return Question.from_dict(response.json())

    def list(
        self,
    ) -> List[Question]:
        """
        List Questions.

        Returns:
            A list of Questions.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [Question.from_dict(evaluation_config) for evaluation_config in response.json()]

