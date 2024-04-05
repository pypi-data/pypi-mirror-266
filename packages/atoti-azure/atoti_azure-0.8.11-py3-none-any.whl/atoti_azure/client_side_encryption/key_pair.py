import atoti as tt
from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class AzureKeyPair(tt.KeyPair, tt.ClientSideEncryptionConfig):
    """Key pair to use for client side encryption.

    Warning:
        Each encrypted blob must have the metadata attribute ``unencrypted_content_length`` with the unencrypted file size.
        If this is not set, an :guilabel:`Issue while downloading` error will occur.

    Example:
        >>> from atoti_azure import AzureKeyPair
        >>> azure_client_side_encryption = (
        ...     AzureKeyPair(
        ...         key_id="key_id",
        ...         public_key="public_key",
        ...         private_key="private_key",
        ...     ),
        ... )
    """

    key_id: str
    """The ID of the key used to encrypt the blob."""
