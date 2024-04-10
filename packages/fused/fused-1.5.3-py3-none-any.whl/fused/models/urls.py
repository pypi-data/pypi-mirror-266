from typing import Union

from pydantic import AnyUrl


class S3Url(AnyUrl):
    """A validated S3 URL"""

    # This is modeled after upstream here
    # https://github.com/pydantic/pydantic/blob/11f7f9019016659e81c96481ffe5c42637489cf3/pydantic/networks.py#L399-L402
    allowed_schemes = {"s3"}

    __slots__ = ()


class GCSUrl(AnyUrl):
    """A validated GCS URL"""

    # This is modeled after upstream here
    # https://github.com/pydantic/pydantic/blob/11f7f9019016659e81c96481ffe5c42637489cf3/pydantic/networks.py#L399-L402
    allowed_schemes = {"gs"}

    __slots__ = ()


class FileUrl(AnyUrl):
    """A validated file URL"""

    # This is modeled after upstream here
    # https://github.com/pydantic/pydantic/blob/11f7f9019016659e81c96481ffe5c42637489cf3/pydantic/networks.py#L399-L402
    allowed_schemes = {"file"}
    host_required = False

    __slots__ = ()


class FusedIntermediaryUrl(AnyUrl):
    """A validated local dataset URL"""

    # This is modeled after upstream here
    # https://github.com/pydantic/pydantic/blob/11f7f9019016659e81c96481ffe5c42637489cf3/pydantic/networks.py#L399-L402
    allowed_schemes = {"fused_intermediary"}

    __slots__ = ()


class FusedTeamUrl(AnyUrl):
    """A validated local dataset URL"""

    # This is modeled after upstream here
    # https://github.com/pydantic/pydantic/blob/11f7f9019016659e81c96481ffe5c42637489cf3/pydantic/networks.py#L399-L402
    allowed_schemes = {"fd"}
    host_required = False

    __slots__ = ()


DatasetUrl = Union[S3Url, GCSUrl, FileUrl, FusedIntermediaryUrl, FusedTeamUrl]
