from typing import Any, Dict, List

from xoadmin.api.api import XOAPI
from xoadmin.api.error import XOSocketError
from xoadmin.utils import get_logger

logger = get_logger(__name__)


class UserManagement:
    """Manage user operations within Xen Orchestra."""

    def __init__(self, api: XOAPI) -> None:
        self.api = api

    async def list_users(self) -> List[str]:
        """List all users by their API paths."""
        return await self.api.get("rest/v0/users")

    async def get_user_details(self, user_path: str) -> Dict[str, Any]:
        """Fetch detailed information for a user given their API path."""
        user_id = user_path.split("/")[-1]
        return await self.api.get(f"rest/v0/users/{user_id}")

    async def create_user(
        self, email: str, password: str, permission: str = "none"
    ) -> Dict[str, Any]:
        """
        Create a new user with the specified details.
        This method now uses WebSocket and JSON-RPC for user creation.
        """
        # Prepare the parameters for the JSON-RPC call
        params = {"email": email, "password": password, "permission": permission}

        try:
            # Utilize the WebSocket connection from the api instance
            socket = self.api.get_socket()
            await socket.open()  # Ensure the socket is open

            # Make the JSON-RPC call to create the user
            result = await socket.call("user.create", params)

            await socket.close()  # Close the socket after the call

            # Check the result for success or failure
            if "result" in result and result["result"]:
                # Assuming the 'result' contains user information on success
                return result["result"]
            else:
                # Handle potential errors returned by the call
                error_msg = result.get("error", {}).get(
                    "message", "Unknown error during user creation"
                )
                raise XOSocketError(f"Failed to create user: {error_msg}")

        except XOSocketError as e:
            # Log or handle the specific websocket error
            logger.error(f"WebSocket error occurred: {e}")
            raise

        except Exception as e:
            # Catch all for any other unexpected errors
            logger.error(f"Unexpected error occurred: {e}")
            raise

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user by their ID using WebSocket and JSON-RPC.
        """
        try:
            # Prepare the parameters for the JSON-RPC call
            params = {"id": user_id}
            # Utilize the WebSocket connection from the api instance
            socket = self.api.get_socket()
            await socket.open()  # Ensure the socket is open
            # Make the JSON-RPC call to delete the user
            result = await socket.call("user.delete", params)
            await socket.close()  # Close the socket after the call
            # Check the result for success or failure
            if "result" in result and result["result"]:
                # Assuming the 'result' contains success information
                return True
            else:
                # Handle potential errors returned by the call
                error_msg = result.get("error", {}).get(
                    "message", "Unknown error during user deletion"
                )
                raise XOSocketError(f"Failed to delete user: {error_msg}")

        except XOSocketError as e:
            # Log or handle the specific WebSocket error
            logger.error(f"WebSocket error occurred: {e}")
            raise

        except Exception as e:
            # Catch all for any other unexpected errors
            logger.error(f"Unexpected error occurred: {e}")
            raise
