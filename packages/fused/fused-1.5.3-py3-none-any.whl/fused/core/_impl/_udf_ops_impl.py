from typing import Any, Optional

from fused.api.api import FusedAPI
from fused.models.api import UdfJobStepConfig
from fused.models.udf import BaseUdf
from fused.models.udf._eval_result import UdfEvaluationResult
from fused.models.udf.output import Output


def get_step_config_from_server(
    email: Optional[str],
    slug: str,
    cache_key: Any,
    _is_public: bool = False,
) -> UdfJobStepConfig:
    # cache_key is unused
    api = FusedAPI()
    if _is_public:
        obj = api._get_public_udf(slug)
    else:
        obj = api._get_udf(email, slug)
    udf = BaseUdf.parse_raw(obj["udf_body"], content_type="json")

    step_config = UdfJobStepConfig(udf=udf)
    return step_config


def get_github_udf_from_server(
    url: str,
    cache_key: Any,
):
    # cache_key is unused
    # TODO: Do this locally in fused-py
    api = FusedAPI(credentials_needed=False)
    obj = api._get_code_by_url(url)
    udf = BaseUdf.parse_raw(obj["udf_body"], content_type="json")

    step_config = UdfJobStepConfig(udf=udf)
    return step_config


def run_and_get_data(udf, *args, **kwargs):
    # TODO: This is a silly way to do this, because we have to pass parameters in such an odd way
    job = udf(*args, **kwargs)
    result = job.run_local()
    if isinstance(result, (Output, UdfEvaluationResult)):
        return result.data
    else:
        return result
