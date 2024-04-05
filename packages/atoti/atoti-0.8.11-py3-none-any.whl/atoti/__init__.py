from atoti_core import (
    DataType as DataType,
    get_env_flag,
)
from atoti_query import (
    Auth as Auth,
    BasicAuthentication as BasicAuthentication,
    ClientCertificate as ClientCertificate,
    OAuth2ResourceOwnerPasswordAuthentication as OAuth2ResourceOwnerPasswordAuthentication,
    QueryCube as QueryCube,
    QueryHierarchy as QueryHierarchy,
    QueryLevel as QueryLevel,
    QueryMeasure as QueryMeasure,
    QueryResult as QueryResult,
    QuerySession as QuerySession,
    TokenAuthentication as TokenAuthentication,
)

from . import (
    agg as agg,
    array as array,
    experimental as experimental,
    function as function,
    math as math,
    string as string,
)
from ._compose_decorators import compose_decorators as _compose_decorators
from ._decorate_api import decorate_api as _decorate_api
from ._disable_call_validation_env_var_name import (
    DISBALE_CALL_VALIDATION_ENV_VAR_NAME as _DISBALE_CALL_VALIDATION_ENV_VAR_NAME,
)
from ._eula import (  # noqa: N811
    EULA as __license__,  # noqa: F401
    hide_new_eula_message as hide_new_eula_message,
    print_eula_message as _print_eula_message,
)
from ._external_table_identifier import (
    ExternalTableIdentifier as ExternalTableIdentifier,
)
from ._measure_metadata import MeasureMetadata as MeasureMetadata
from ._py4j_utils import patch_databricks_py4j as _patch_databricks_py4j
from ._telemetry import telemeter as _telemeter
from ._user_service_client import UserServiceClient as UserServiceClient
from ._validate_call import validate_call as _validate_call
from .aggregate_provider import AggregateProvider as AggregateProvider
from .app_extension import *
from .client_side_encryption_config import (
    ClientSideEncryptionConfig as ClientSideEncryptionConfig,
)
from .column import Column as Column
from .config import *
from .cube import Cube as Cube
from .directquery import *
from .function import *
from .hierarchy import Hierarchy as Hierarchy
from .level import Level as Level
from .measure import Measure as Measure
from .order import *
from .scope import *
from .session import Session as Session
from .table import Table as Table
from .type import *

_print_eula_message()


_patch_databricks_py4j()

_api_decorators = []

_track_call = _telemeter()

if _track_call:
    _api_decorators.append(_track_call)

if __debug__ and not get_env_flag(_DISBALE_CALL_VALIDATION_ENV_VAR_NAME):
    _api_decorators.append(_validate_call)

if _api_decorators:
    _decorate_api(_compose_decorators(*_api_decorators))
