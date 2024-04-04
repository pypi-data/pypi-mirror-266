import os
import json
import requests
import aiohttp
import mimetypes
from aiohttp import FormData
from dataclasses import dataclass
from typing import Optional, List, Union
from trufflepig._constants import SERVER_ADDRESS


@dataclass
class SearchResult:
    """
    Result of a search.

    Attributes:
        content (str): Content of the search result.
        document_key (str): Key of the document from which the content originated.
        score (float): Similarity score to search query.
        metadata (dict): Metadata associated with the document.
        page (int): Page number of the document from which the content originated.
    """

    content: str
    document_key: str
    score: float
    metadata: dict
    page: int

@dataclass
class UploadTrackingResult:
    """
    The tracking status of a data upload request.

    Attributes:
        document_key (str): The uploaded document's key.
        job_status (str): The status of an upload job (IN PROGRESS, SUCCESS, FAILED)
        start_time (int): The epoch timestamp of the initial upload request.
        end_time (str): The epoch timestamp of when the upload request reached a terminal state.
    """

    document_key: str
    job_status: str
    start_time: int
    end_time: int


class Index:
    def __init__(self, api_key: str, index_name: str):
        """
        Initialize a new Index object for interacting with an existing trufflepig search index.

        Parameters:
        -----------
        api_key: str
            The API key to be used for authenticating requests made using the trufflepig client.
        index_name: str
            The name of the index being accessed.

        Example:
        -----------
        ```python
        index = Index("my-api-key", "my-index")
        ```
        """
        self.index_name = index_name
        self._api_key = api_key

    def __str__(self):
        return f"Index(index_name={self.index_name})"

    def upload(
        self,
        text: Optional[List[dict]] = None,
        files: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        Upload data to your trufflepig index!

        Currently supported data types:
        - strings
        - files with the following mimetypes:
            - application/pdf
            - text/plain

        Only one of text or files can be provided.

        Parameters:
        -----------
        text: `Optional[List[dict]`
            Text data to be uploaded to the search index. Each item in the list should be a dictionary with the following keys:

                - `document_key` (required): str

                - `document` (required): str
                
                - `metadata` (`Optional[dict]`): Metadata associated with the document.
        files: `Optional[List[dict]`
            Files to be uploaded to the search index. Each item in the list should be a dictionary with the following keys:

                - `file_path` (required): str

                - `metadata` (`Optional[dict]`): Metadata associated with the file.

            For files, the document key is the file name.

        Returns:
        -----------
        List[str]: A list of document keys for the upload job(s).

        Example:
        -----------
        ### Uploading text data
        ```python
        text_data = [
            {
                "document_key": "unique_key_1",
                "document": "This is the first document content.",
                "metadata": {"author": "Author Name", "date": "2023-04-01"}
            },
            {
                "document_key": "unique_key_2",
                "document": "This is the second document content.",
                "metadata": {"author": "Another Author", "date": "2023-04-02"}
            }
        ]
        document_keys = index.upload(text=text_data)
        ```

        ### Uploading files
        ```python
        files_data = [
            {
                "document_path": "path/to/your/file1.pdf",
                "metadata": {"title": "File 1 Title", "year": "2023"}
            },
            {
                "document_path": "path/to/your/file2.pdf",
                "metadata": {"title": "File 2 Title", "year": "2023"}
            }
        ]
        document_keys = index.upload(files=files_data)
        ```
        """
        if (text and files and len(files) > 0) or (
            not text and (not files or len(files) == 0)
        ):
            raise ValueError("Must set one and only one of text or files.")
        if files and len(files) > 0:
            file_list = []
            open_files= []
            try:
                for file_info in files:
                    file_path = file_info["document_path"]
                    if not os.path.isfile(file_path):
                        raise ValueError(f"Invalid file path: {file_path}")

                    file_name = os.path.basename(file_path)
                    mime_type = mimetypes.guess_type(file_path)[0]

                    file_content = open(file_path, "rb")
                    open_files.append(file_content)
                    file_list.append(("files", (file_name, file_content, mime_type)))

                    metadata = json.dumps(file_info.get("metadata", {}))
                    file_list.append(("metadata", (None, metadata, 'application/json')))

                response = requests.post(
                    f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/upload",
                    headers={"x-api-key": self._api_key},
                    files=file_list
                )

                for _, file_tuple in file_list:
                    if hasattr(file_tuple[1], 'close'):
                        file_tuple[1].close()

                if response.status_code == 200:
                    return response.json()["document_keys"]
                else:
                    raise Exception(f"{response.status_code} Error: {response.text}")
            finally:
                for f in open_files:
                    f.close()
        if text:
            if isinstance(text, str):
                text = [text]
            elif not isinstance(text, list):
                raise ValueError("Data must be either a list of strings or a string.")
            
            text_data = [
                {
                    "document_key": text_item.get("document_key", None),
                    "document": text_item["document"],
                    "metadata": text_item.get("metadata", {})
                }
                for text_item in text
            ]

            json_data = {"text": text_data}

            response = requests.post(
                f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/upload",
                json=json_data,
                headers={"x-api-key": self._api_key},
            )
            if response.status_code == 200:
                return response.json()["document_keys"]
            else:
                raise Exception(f"{response.status_code} Error: {response.text}")

    def search(
        self, query_text: str, max_results: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Search your trufflepig index for relevant data!

        Parameters:
        -----------
        query_text: str
            A search query.
        max_results: Optional[int] = None
            Maximum number of relevant results to be returned.

        Returns:
        -----------
        List[SearchResult]: A list of search result objects, each containing the content of the document, the document key, the similarity score, any metadata associated with the document, and the page number of the document from which the content originated (if applicable).

        Example:
        -----------
        ```python
        search_results = index.search(query_text='What is a truffle pig?')
        ```
        """
        url = f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/search"
        headers = {"x-api-key": self._api_key}
        params = {"query_text": query_text, "max_results": max_results}

        response = requests.post(url, params=params, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            return [
                SearchResult(
                    content=item["content"],
                    document_key=item["document_key"],
                    score=item["score"],
                    metadata=item["metadata"],
                    page=item.get("page")
                )
                for item in response_json
            ]
        else:
            raise Exception(f"{response.status_code} Error: {response.content}")

    def get_upload_status(self, document_keys: List[str]) -> List[UploadTrackingResult]:
        """
        Fetch statuses of upload jobs by document keys provided in upload response.

        Parameters:
        -----------
        document_keys: List[str]
             A list of document keys corresponding to uploaded documents.

        Returns:
        -----------
        List[UploadTrackingResult]: list of UploadTrackingResult dataclass, each item containing the document key, job status, start time, and end time of the upload job.

        Example:
        -----------
        ```python
        tracking_results = client.get_upload_status(['document_key_1'])
        print(tracking_results.job_status)
        ```
        """
        if len(document_keys) < 1:
            raise ValueError("must provide at least 1 document_key.")

        # send http request
        response = requests.post(
            f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/upload_status",
            headers={"x-api-key": self._api_key},
            json={"document_keys": document_keys},
        )

        if response.status_code == 200:
            result = response.json()
            return [
                UploadTrackingResult(
                    document_key=item["document_key"],
                    job_status=item["job_status"],
                    start_time=item["start_time"],
                    end_time=item["end_time"],
                )
                for item in result
            ]
        else:
            raise Exception(f"{response.status_code} Error: {response.text}")
        

    def delete_documents(self, document_keys: List[str]) -> bool:
        """
        Delete documents from your trufflepig index.

        Parameters:
        -----------
        document_keys: List[str]
            A list of document keys corresponding to documents to be deleted.

        Returns:
        -----------
        bool: True if the documents were successfully deleted, False otherwise.

        Example:
        -----------
        ```python
        is_deleted = index.delete_documents(['document_key_1'])
        ```
        """
        try:
            response = requests.post(
                f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/documents/delete",
                headers={"x-api-key": self._api_key},
                json={"document_keys": document_keys},
            )
            if response.status_code == 200:
                return "message" in response.json()
            else:
                raise Exception(f"{response.status_code} Error: {response.content}")
        except Exception as e:
            raise e
        

    def list_documents(self) -> List[str]:
        """
        List all documents in your trufflepig index.

        Returns:
        -----------
        List[str]: A list of document keys.

        Example:
        -----------
        ```python
        document_keys = index.list_documents()
        ```
        """
        try:
            response = requests.get(
                f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/documents",
                headers={"x-api-key": self._api_key},
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"{response.status_code} Error: {response.content}")
        except Exception as e:
            raise e
        

    async def upload_async(
        self,
        text: Optional[List[dict]] = None,
        files: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        Upload data to your trufflepig index!

        Currently supported data types:
        - strings
        - files with the following mimetypes:
            - application/pdf
            - text/plain

        Only one of text or files can be provided.

        Parameters:
        -----------
        text: `Optional[List[dict]`
            Text data to be uploaded to the search index. Each item in the list should be a dictionary with the following keys:

                - `document_key` (required): str

                - `document` (required): str
                
                - `metadata` (`Optional[dict]`): Metadata associated with the document.
        files: `Optional[List[dict]`
            Files to be uploaded to the search index. Each item in the list should be a dictionary with the following keys:

                - `document_path` (required): str

                - `metadata` (`Optional[dict]`): Metadata associated with the file.

            For files, the document key is the file name.

        Returns:
        -----------
        List[str]: A list of document keys for the upload job(s).

        Example:
        -----------
        ### Uploading text data
        ```python
        text_data = [
            {
                "document_key": "unique_key_1",
                "document": "This is the first document content.",
                "metadata": {"author": "Author Name", "date": "2023-04-01"}
            },
            {
                "document_key": "unique_key_2",
                "document": "This is the second document content.",
                "metadata": {"author": "Another Author", "date": "2023-04-02"}
            }
        ]
        document_keys = await index.upload_async(text=text_data)
        ```

        ### Uploading files
        ```python
        files_data = [
            {
                "document_path": "path/to/your/file1.pdf",
                "metadata": {"title": "File 1 Title", "year": "2023"}
            },
            {
                "document_path": "path/to/your/file2.pdf",
                "metadata": {"title": "File 2 Title", "year": "2023"}
            }
        ]
        document_keys = await index.upload_async(files=files_data)
        ```
        """
        if (text and files and len(files) > 0) or (
            not text and (not files or len(files) == 0)
        ):
            raise ValueError("Must set one and only one of text or files.")

        if files and len(files) > 0:
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                file_objects = []  # Keep track of file objects to close them later
                try:
                    for file_info in files:
                        file_path = file_info["document_path"]
                        if not os.path.isfile(file_path):
                            raise ValueError(f"Invalid file path: {file_path}")

                        file_name = os.path.basename(file_path)
                        mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

                        file_object = open(file_path, "rb")
                        file_objects.append(file_object)  # Add the file object to the list

                        data.add_field("files", file_object, filename=file_name, content_type=mime_type)

                        metadata = file_info.get("metadata", {})
                        if metadata:  # Only add metadata if it's not empty
                            data.add_field("metadata", json.dumps(metadata), content_type='application/json')

                    async with session.post(
                        f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/upload",
                        headers={"x-api-key": self._api_key},
                        data=data,
                    ) as response:
                        if response.status == 200:
                            return (await response.json())["document_keys"]
                        else:
                            raise Exception(f"{response.status} Error: {await response.text()}")
                finally:
                    for file_object in file_objects:
                        file_object.close()
        if text:
            text_data = [
                {
                    "document_key": text_item.get("document_key", None),
                    "document": text_item["document"],
                    "metadata": text_item.get("metadata", {})
                }
                for text_item in text
            ]

            json_data = {"text": text_data}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/upload",
                    json=json_data,
                    headers={"x-api-key": self._api_key},
                ) as response:
                    if response.status == 200:
                        return (await response.json())["document_keys"]
                    else:
                        raise Exception(
                            f"{response.status} Error: {await response.text()}"
                        )

    async def search_async(
        self,
        query_text: str,
        max_results: Optional[int] = None,
    ):
        """
        Asynchronously search your trufflepig index for relevant data!

        Parameters:
        -----------
        query_text: str
            A search query.
        max_results: Optional[int] = None
            Maximum number of relevant results to be returned.

        Returns:
        -----------
        List[SearchResult]: A list of search result objects, each containing the content of the document, the document key, the similarity score, any metadata associated with the document, and the page number of the document from which the content originated (if applicable).

        Example:
        -----------
        ```python
        search_results = await index.search(query_text='What is a truffle pig?')
        ```
        """
        url = f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/search"
        params = {k: v for k, v in {"query_text": query_text, "max_results": max_results}.items() if v is not None}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers={"x-api-key": self._api_key}, params=params
            ) as response:
                if response.status == 200:
                    return [
                        SearchResult(
                            content=item["content"],
                            document_key=item["document_key"],
                            score=item["score"],
                            metadata=item["metadata"],
                            page=item.get("page")
                        )
                        for item in await response.json()
                    ]
                else:
                    raise Exception(f"{response.status} Error: {await response.text()}")

    async def get_upload_status_async(
        self, document_keys: List[str]
    ) -> List[UploadTrackingResult]:
        """
        Asynchronously fetch statuses of upload jobs using their document_keys.

        Parameters:
        -----------
        document_keys: List[str]
            A list of document_keys corresponding to upload jobs.

        Returns:
        -----------
        List[UploadTrackingResult]: list of UploadTrackingResult dataclass, each item containing the document key, job status, start time, and end time of the upload job.

        Example:
        -----------
        ```python
        tracking_results = await client.get_upload_status(['document_key_1'])
        print(tracking_results.job_status)
        ```
        """
        if len(document_keys) < 1:
            raise ValueError("must provide at least 1 document_key.")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/upload_status",
                headers={"x-api-key": self._api_key},
                json={"document_keys": document_keys},
            ) as response:
                if response.status == 200:
                    response_json = await response.json()
                    return [
                        UploadTrackingResult(
                            document_key=item["document_key"],
                            job_status=item["job_status"],
                            start_time=item["start_time"],
                            end_time=item["end_time"],
                        )
                        for item in response_json
                    ]
                else:
                    raise Exception(f"{response.status} Error: {await response.text()}")
                
    async def delete_documents_async(self, document_keys: List[str]) -> bool:
        """
        Asynchronously delete documents from your trufflepig index.

        Parameters:
        -----------
        document_keys: List[str]
            A list of document keys corresponding to documents to be deleted.

        Returns:
        -----------
        bool: True if the documents were successfully deleted, False otherwise.

        Example:
        -----------
        ```python
        is_deleted = await index.delete_documents_async(['document_key_1'])
        ```
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/documents/delete",
                    headers={"x-api-key": self._api_key},
                    json={"document_keys": document_keys},
                ) as response:
                    if response.status == 200:
                        return "message" in await response.json()
                    else:
                        raise Exception(f"{response.status} Error: {await response.text()}")
        except Exception as e:
            raise e
        
    
    async def list_documents_async(self) -> List[str]:
        """
        Asynchrounously list all documents in your trufflepig index.

        Returns:
        -----------
        List[str]: A list of document keys.

        Example:
        -----------
        ```python
        document_keys = await index.list_documents_async()
        ```
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{SERVER_ADDRESS}/v0/indexes/{self.index_name}/documents",
                    headers={"x-api-key": self._api_key},
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"{response.status} Error: {await response.text()}")
        except Exception as e:
            raise e
