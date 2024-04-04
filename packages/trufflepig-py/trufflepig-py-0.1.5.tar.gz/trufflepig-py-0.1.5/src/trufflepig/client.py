import requests
from typing import List

from trufflepig.index import Index
from trufflepig._constants import SERVER_ADDRESS


class Trufflepig:
    """Trufflepig client class"""

    def __init__(
        self,
        api_key: str,
    ):
        """
        Client object constructor.

        Parameters:
        -----------
        api_key: str
            The API key to be used for authenticating requests made using the trufflepig client.

        Example:
        -----------
        client = Trufflepig("your-api-key")
        """
        self.api_key = api_key

    def create_index(self, index_name: str) -> Index:
        """
        Create a new index.

        Parameters:
        -----------
        index_name: str
            The name of the index being created.

        Returns:
        -----------
        Index: A search index.

        Example:
        -----------
        index = trufflepig.create_index("myIndex")
        """
        # send http request
        response = requests.put(
            f"http://{SERVER_ADDRESS}/v0/indexes/{index_name}",
            headers={"x-api-key": self.api_key},
        )

        if response.status_code == 201:
            return Index(api_key=self.api_key, index_name=index_name)
        else:
            raise Exception(f"{response.status_code} Error: {response.text}")

    def get_index(self, index_name: str) -> Index:
        """
        Get an existing index.

        Parameters:
        -----------
        index_name: str
            The name of the index being created.

        Returns:
        -----------
        Index: A search index.

        Example:
        -----------
        index = trufflepig.get_index("myIndex")
        """
        return Index(self.api_key, index_name)

    def list_indexes(self) -> List[Index]:
        """
        List indexes available to this user.

        Returns:
        -----------
        List[Index]

        Example:
        -----------
        indexes = trufflepig.list_indexes()
        """
        # send http request
        response = requests.get(
            f"http://{SERVER_ADDRESS}/v0/indexes", headers={"x-api-key": self.api_key}
        )

        # check the response
        if response.status_code == 200:
            indexes_data = response.json()
            indexes = [
                Index(api_key=self.api_key, index_name=data["index_name"])
                for data in indexes_data
            ]
            return indexes
        else:
            # Handle errors (e.g., 500 Internal Server Error)
            raise Exception(f"{response.status_code} Error: {response.text}")

    def delete_index(self, index_name: str) -> bool:
        """
        Delete an index by name.

        Parameters:
        -----------
        index_name: str
            The name of the index being deleted.

        Returns:
        -----------
        boolean: True, if index was deleted.

        Example:
        -----------
        is_deleted = trufflepig.delete_index('index name')
        """
        response = requests.delete(
            f"http://{SERVER_ADDRESS}/v0/indexes/{index_name}",
            headers={"x-api-key": self.api_key},
        )

        if response.status_code == 200:
            result = response.json()
            return "message" in result.keys()
        else:
            # Log or handle unexpected errors here
            raise Exception(f"{response.status_code} Error: {response.text}")
