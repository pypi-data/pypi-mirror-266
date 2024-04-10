from typing import Optional
from scale_egp.sdk.types.user_info import UserInfoResponse

from scale_egp.utils.api_utils import APIEngine


class UsersCollection(APIEngine):
    """
    Collections class for Scale EGP users.
    """

    _sub_path = "users"

    def who_am_i(self) -> UserInfoResponse:
        """
        Get the currently authenticated user.

        Returns:
            The currently authenticated user.
        """
        response = self._get(sub_path="user-info")
        return UserInfoResponse.from_dict(response.json())

    def get(self, id: str) -> UserInfoResponse:
        """
                Get a user by ID.

                Args:
                    id: The ID of the user.
        >
                Returns:
                    The user.
        """
        response = self._get(sub_path=f"{self._sub_path}/{id}")
        return UserInfoResponse.from_dict(response.json())

    def get_default_account_id(self) -> Optional[str]:
        user_info = self.who_am_i()
        candidates = [u.account.id for u in user_info.accounts if u.role == "admin"]
        if len(candidates) > 0:
            return candidates[0]
        # No account with admin role found. This shouldn't happen as each
        # user should have a personal account, but if this does happen,
        # we can return the first account in the list
        if len(user_info.accounts) > 0:
            return user_info.accounts[0].account.id
        # No default account could be identified
        return None
