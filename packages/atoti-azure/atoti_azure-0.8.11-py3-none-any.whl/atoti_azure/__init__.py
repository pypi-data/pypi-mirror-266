r"""Plugin to load CSV and parquet files from Azure Blob Storage into Atoti tables.

This package is required to load files with path like ``https://{ACCOUNT_NAME}.blob.core.windows.net/path/to/data-*``.

Authentication is done with a `connection string <https://docs.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string?toc=/azure/storage/blobs/toc.json#store-a-connection-string>`__ that will be read from the ``AZURE_CONNECTION_STRING`` environment variable or, if it does not exist, from the file at ``~/.azure/credentials`` (``C:\\Users\\{USERNAME}\\.azure\\credentials`` on Windows).

Example:
    >>> table = session.read_csv(
    ...     "https://atotipubliccsv.blob.core.windows.net/csv/city.csv", keys=["city"]
    ... )
    >>> table.head().sort_index()
            value
    city
    London  200.0
    Paris   100.0

"""

from .client_side_encryption import *
