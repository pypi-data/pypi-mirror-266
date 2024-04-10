from typing import List, Optional


from scale_egp.sdk.types.question_sets import QuestionSet, QuestionSetRequest
from scale_egp.sdk.types.questions import Question
from scale_egp.utils.api_utils import (
    APIEngine,
)


class QuestionSetCollection(APIEngine):
    _sub_path = "v2/question-sets"

    def create(
        self,
        name: str,
        questions: List[Question],
        account_id: Optional[str] = None,
    ) -> QuestionSet:
        """
        Create a new Question Set.

        Args:
            name: The name of the Question Set.
            questions: The questions in this Question Set.
            account_id: The ID of the account to create this Question Set for.
        Returns:
            The newly created Evaluation Configuration.
        """
        response = self._post(
            sub_path=self._sub_path,
            request=QuestionSetRequest(
                name=name,
                account_id=account_id or self._api_client.account_id,
                question_ids=[question.id for question in questions],
            ),
        )
        return QuestionSet.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> QuestionSet:
        """
        Get the details of a Question Set.

        Args:
            id: The ID of the Question Set.

        Returns:
            The details of the Question Set.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return QuestionSet.from_dict(response.json())

    def list(
        self,
    ) -> List[QuestionSet]:
        """
        List Question Sets.

        Returns:
            A list of Question Sets.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [QuestionSet.from_dict(question_set) for question_set in response.json()]
