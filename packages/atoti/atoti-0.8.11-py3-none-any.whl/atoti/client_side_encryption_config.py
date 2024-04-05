from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ClientSideEncryptionConfig:
    """Parameters to use for client side encryption.

    The following client side encryptions are supported:

    * :mod:`atoti-aws <atoti_aws>` plugin:

      * :class:`atoti_aws.AwsKeyPair`.
      * :class:`atoti_aws.AwsKmsConfig`.

    * :mod:`atoti-azure <atoti_azure>` plugin :

      * :class:`atoti_azure.AzureKeyPair`.

    """
