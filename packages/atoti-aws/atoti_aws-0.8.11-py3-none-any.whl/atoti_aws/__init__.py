"""Plugin to load CSV and Parquet files from AWS S3 into Atoti tables.

This package is required to load files with paths starting with ``s3://``.

Authentication is handled by the underlying AWS SDK for Java library.
Refer to their `documentation <https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html#setup-credentials-setting>`__  for the available options.

Example:
    >>> table = session.read_csv("s3://test.public.atoti.io/city.csv", keys=["city"])
    >>> table.head().sort_index()
            value
    city
    London  200.0
    Paris   100.0

"""

from ._s3_ping_discovery_protocol import (
    S3PingDiscoveryProtocol as S3PingDiscoveryProtocol,
)
from .client_side_encryption import *
