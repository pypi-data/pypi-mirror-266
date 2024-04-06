# MotionLake Client

MotionLake Client is a Python client library for interacting with a storage server designed for a new mobility data lake solution. It provides functionalities to create collections, store data, query data, and retrieve collections.

## Installation

You can install the library via pip:

```bash
pip install motion-lake-client
```

## Usage

Here's a brief overview of how to use the library:

```python
from motion_lake_client import BaseClient

# Initialize the client with the base URL of the storage server
client = BaseClient(lake_url='http://localhost:8000')

# Create a new collection
client.create_collection('my_collection')

# Store data in a collection
data = b'example_data'
timestamp = int(datetime.now().timestamp())
client.store('my_collection', data, timestamp)

# Query data from a collection
results = client.query('my_collection', min_timestamp=0, max_timestamp=timestamp, ascending=True)

# Retrieve last item from a collection
last_item = client.get_last_item('my_collection')

# Retrieve first item from a collection
first_item = client.get_first_item('my_collection')

# Get items between two timestamps
items_between = client.get_items_between('my_collection', min_timestamp=0, max_timestamp=timestamp)

# Get items before a timestamp
items_before = client.get_items_before('my_collection', timestamp, limit=10)

# Get items after a timestamp
items_after = client.get_items_after('my_collection', timestamp, limit=10)

# Get all collections
collections = client.get_collections()
```

## Documentation

For detailed documentation and examples, please refer to the [official documentation](https://your-documentation-url.com).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any bugs or feature requests.

## License

All rights reserved.