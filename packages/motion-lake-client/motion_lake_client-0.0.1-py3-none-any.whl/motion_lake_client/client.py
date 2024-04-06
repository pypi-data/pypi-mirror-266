import dataclasses
from datetime import datetime
from typing import Protocol, Dict, Any, List

import requests

@dataclasses.dataclass
class Item:
    """
    A data item in the collection.
    """
    timestamp: datetime
    data: bytes


@dataclasses.dataclass
class Collection:
    """
    A summary of a collection. A collection is a group of items.
    """
    name: str
    min_timestamp: datetime
    max_timestamp: datetime
    count: int


class NetworkClient(Protocol):
    """
    A network client to make requests to the storage server.
    """

    def get(self, url: str, query_params: Dict[str, Any] = None) -> dict:
        ...

    def post(self, url: str, body: dict) -> dict:
        ...


class RequestsClient(NetworkClient):
    """
    A network client using the requests library.
    """

    def __init__(self, base_url: str, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url

    def get(self, url: str, query_params: Dict[str, Any] = None) -> dict:
        response = requests.get(self.base_url + url, params=query_params)
        return response.json()

    def post(self, url: str, body: dict) -> dict:
        response = requests.post(self.base_url + url, json=body)
        return response.json()


class InnerClient:
    def __init__(self, network_client: NetworkClient):
        self.network_client = network_client

    def create_collection(self, collection_name: str) -> dict:
        """
        Create a new collection with the given name.
        :param collection_name: The name of the collection to create
        :return: None
        """
        return self.network_client.post(f"/collection/", {"name": collection_name})

    def store(self, collection_name: str, data: bytes, timestamp: int, content_type: str = None) -> dict:
        """
        Store the given data in the collection with the given name.
        :param collection_name: The name of the collection to store the data in
        :param data: The data to store
        :param timestamp: The timestamp to associate with the data
        :param content_type: The type of the data
        :return: None
        """
        return self.network_client.post(
            f"/store/{collection_name}/",
            {"data": data.hex(), "timestamp": timestamp, "content_type": content_type}
        )

    def query(self, collection_name: str, min_timestamp: int, max_timestamp: int, ascending: bool,
              limit: int = None, offset: int = None) -> dict:
        """
        Query the data in the collection with the given name.
        :param collection_name: The name of the collection to query
        :param min_timestamp: The minimum timestamp to filter the data
        :param max_timestamp: The maximum timestamp to filter the data
        :param ascending: Whether to sort the data in ascending order
        :param limit: The limit of the data to retrieve
        :param offset: The offset of the data to retrieve
        :return: The data in the collection as a list of tuples of bytes and datetime
        """
        return self.network_client.get(
            f"/query/{collection_name}/",
            {
                "min_timestamp": min_timestamp,
                "max_timestamp": max_timestamp,
                "ascending": ascending,
                "limit": limit,
                "offset": offset
            }
        )

    def get_collections(self) -> List[Collection]:
        """
        Get a list of all collections.
        :return: A list of collections
        """
        collections = self.network_client.get("/collections/")
        return [
            Collection(
                name=collection["name"],
                min_timestamp=datetime.fromisoformat(collection["min_timestamp"]) if collection[
                    "min_timestamp"] else None,
                max_timestamp=datetime.fromisoformat(collection["max_timestamp"]) if collection[
                    "max_timestamp"] else None,
                count=collection["count"]
            )
            for collection in collections
        ]


class BaseClient:
    def __init__(self, lake_url: str = 'http://localhost:8000'):
        """
        Initialize the client with the base URL of the storage server.
        :param lake_url: The base URL of the storage server
        """
        self.inner_client = InnerClient(RequestsClient(lake_url))

    @staticmethod
    def _parse_server_timestamp(timestamp: int) -> datetime:
        return datetime.fromtimestamp(timestamp / 1000)

    def _parse_results(self, results: List[dict]) -> List[Item]:
        return [
            Item(
                timestamp=self._parse_server_timestamp(item["timestamp"]),
                data=bytes.fromhex(item["data"])
            )
            for item in results
        ]

    def create_collection(self, collection_name: str) -> dict:
        return self.inner_client.create_collection(collection_name)

    def store(self, collection_name: str, data: bytes, timestamp: int, content_type: str = None) -> dict:
        return self.inner_client.store(collection_name, data, timestamp, content_type)

    def query(self, collection_name: str, min_timestamp: int, max_timestamp: int, ascending: bool,
              limit: int = None, offset: int = 0) -> dict:
        return self.inner_client.query(collection_name, min_timestamp, max_timestamp, ascending, limit, offset)

    def get_last_items(self, collection_name: str, limit: int) -> List[Item]:
        response = self.query(collection_name, 0, int(datetime.now().timestamp()), False, limit)
        return self._parse_results(response['results'])

    def get_last_item(self, collection_name: str) -> Item:
        return self.get_last_items(collection_name, 1)[0]

    def get_first_items(self, collection_name: str, limit: int) -> List[Item]:
        response = self.query(collection_name, 0, int(datetime.now().timestamp()), True, limit)
        return self._parse_results(response['results'])

    def get_first_item(self, collection_name: str) -> Item:
        return self.get_first_items(collection_name, 1)[0]

    def get_items_between(self, collection_name: str, min_timestamp: int, max_timestamp: int, ascending: bool = True,
                          limit: int = None, offset: int = None) -> List[Item]:
        response = self.query(collection_name, min_timestamp, max_timestamp, ascending, limit, offset)
        return self._parse_results(response['results'])

    def get_items_before(self, collection_name: str, timestamp: int, limit: int) -> List[Item]:
        return self.get_items_between(collection_name, 0, timestamp, False, limit)

    def get_items_after(self, collection_name: str, timestamp: int, limit: int) -> List[Item]:
        return self.get_items_between(collection_name, timestamp, int(datetime.now().timestamp()), True, limit)

    def get_collections(self) -> List[Collection]:
        return self.inner_client.get_collections()
