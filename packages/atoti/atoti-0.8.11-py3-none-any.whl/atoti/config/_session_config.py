from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal, Optional

from atoti_core import (
    PYDANTIC_CONFIG as _PYDANTIC_CONFIG,
    FrozenMapping,
    FrozenSequence,
    frozendict,
    keyword_only_dataclass,
)
from pydantic import PlainSerializer
from pydantic.dataclasses import dataclass

from .authentication._authentication_config import AuthenticationConfig
from .branding_config import BrandingConfig
from .client_certificate_config import ClientCertificateConfig
from .https_config import HttpsConfig
from .i18n_config import I18nConfig
from .jwt_config import JwtConfig
from .logging_config import LoggingConfig
from .user_content_storage_config import UserContentStorageConfig


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class SessionConfig:
    app_extensions: Annotated[
        FrozenMapping[str, Path],
        PlainSerializer(
            lambda app_extensions: app_extensions
            or None  # Remove empty mapping because the community edition does not allow this config option.
        ),
    ] = frozendict()

    authentication: Optional[AuthenticationConfig] = None

    branding: Optional[BrandingConfig] = None

    client_certificate: Optional[ClientCertificateConfig] = None

    extra_jars: FrozenSequence[Path] = ()

    https: Optional[HttpsConfig] = None

    i18n: Optional[I18nConfig] = None

    java_options: FrozenSequence[str] = ()

    jwt: Optional[JwtConfig] = None

    logging: Optional[LoggingConfig] = None

    port: int = 0

    ready: bool = True

    same_site: Optional[Literal["none", "strict"]] = None

    user_content_storage: Optional[UserContentStorageConfig] = None
