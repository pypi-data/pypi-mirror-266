from typing import Any, Optional, List, Dict

import httpx

from scale_egp.sdk.types.evaluation_configs import EvaluationConfig, EvaluationConfigRequest
from scale_egp.sdk.types.question_sets import QuestionSet
from scale_egp.utils.api_utils import (
    APIEngine,
)
from scale_egp.sdk.enums import EvaluationType


class EvaluationConfigCollection(APIEngine):
    _sub_path = "v2/evaluation-configs"

    def create(
        self,
        evaluation_type: EvaluationType,
        question_set: QuestionSet,
        account_id: Optional[str] = None,
    ) -> EvaluationConfig:
        """
        Create a new Evaluation Configuration.

        Args:
            evaluation_type: The type of Evaluation. Only `HUMAN` is supported.
            question_set: The Question Set to associate with the Evaluation.
            account_id: The ID of the account to create this Evaluation Configuration for.

        Returns:
            The newly created Evaluation Configuration.
        """
        response = self._post(
            sub_path=self._sub_path,
            request=EvaluationConfigRequest(
                evaluation_type=evaluation_type.value,
                question_set_id=question_set.id,
                account_id=account_id or self._api_client.account_id,
            ),
        )
        return EvaluationConfig.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> EvaluationConfig:
        """
        Get the details of an evaluation config.

        Args:
            id: The ID of the Evaluation Configuration.

        Returns:
            The Evaluation Configuration.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return EvaluationConfig.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Delete an Evaluation Configuration.

        Args:
            id: The ID of the Evaluation Configuration.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
    ) -> List[EvaluationConfig]:
        """
        List Evaluation Configurations.

        Returns:
            A list of Evaluation Configurations.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        return [EvaluationConfig.from_dict(evaluation_config) for evaluation_config in response.json()]

