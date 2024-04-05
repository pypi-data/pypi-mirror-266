import atoti as tt
from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass

from ._client_side_encryption import AwsClientSideEncryption


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class AwsKmsConfig(AwsClientSideEncryption, tt.ClientSideEncryptionConfig):
    """KMS configuration to use for `client side encryption <https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingClientSideEncryption.html>`__.

    The AWS KMS CMK must have been created in the same AWS region as the destination bucket (Cf. `AWS documentation <https://docs.aws.amazon.com/AmazonS3/latest/dev/replication-config-for-kms-objects.html>`__).

    Example:
        >>> from atoti_aws import AwsKmsConfig
        >>> client_side_encryption_config = (
        ...     AwsKmsConfig(
        ...         region="eu-west-3",
        ...         key_id="key_id",
        ...     ),
        ... )
    """

    key_id: str
    """The ID to identify the key in KMS."""
