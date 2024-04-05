import atoti as tt
from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass

from ._client_side_encryption import AwsClientSideEncryption


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class AwsKeyPair(tt.KeyPair, AwsClientSideEncryption, tt.ClientSideEncryptionConfig):
    """Key pair to use for `client side encryption <https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingClientSideEncryption.html>`__.

    Example:
        >>> from atoti_aws import AwsKeyPair
        >>> client_side_encryption_config = (
        ...     AwsKeyPair(
        ...         region="eu-west-3",
        ...         private_key="private_key",
        ...         public_key="public_key",
        ...     ),
        ... )
    """
