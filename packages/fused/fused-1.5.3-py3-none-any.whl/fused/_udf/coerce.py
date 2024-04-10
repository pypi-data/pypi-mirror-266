from __future__ import annotations

from typing import Union
from uuid import UUID

from fused.models import (
    JoinJobStepConfig,
    JoinSinglefileJobStepConfig,
    MapJobStepConfig,
    UdfJobStepConfig,
)
from fused.models.api.dataset import JobMetadata, Table
from fused.models.udf import BaseUdf


def _fetch_udf_from_string(s: str) -> BaseUdf:
    assert "gist.github.com" in s, f"'{s}' is not a GitHub Gist URL."
    gist_id = s.split("/")[-1]
    try:
        # Note that a github gist ID is an SHA hash, not a UUID, but they both have the
        # same number of bits as a hex string so this is easy validation.
        UUID(gist_id)
    except ValueError:
        raise ValueError(f"Could not parse '{s}' as a GitHub Gist URL")

    return BaseUdf.from_gist(gist_id)


CoerceableToUdf = Union[
    BaseUdf,
    dict,
    MapJobStepConfig,
    JoinJobStepConfig,
    JoinSinglefileJobStepConfig,
    UdfJobStepConfig,
    JobMetadata,
    Table,
]


def coerce_to_udf(udf: CoerceableToUdf) -> BaseUdf:
    if isinstance(udf, BaseUdf):
        return udf
    elif isinstance(udf, MapJobStepConfig):
        return udf.udf
    elif isinstance(udf, JoinJobStepConfig):
        return udf.udf
    elif isinstance(udf, JoinSinglefileJobStepConfig):
        return udf.udf
    elif isinstance(udf, UdfJobStepConfig):
        return udf.udf
    elif isinstance(udf, JobMetadata):
        return udf.udf
    elif isinstance(udf, Table):
        return udf.parent.udf
    else:
        return BaseUdf.parse_obj(udf)
