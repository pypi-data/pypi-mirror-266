from ..input_helpers import get_org_from_input_or_ctx
from ..context import get_apiclient_from_ctx
from ..input_helpers import strip_none


def get_api(ctx):
    return get_apiclient_from_ctx(ctx).policy_config_api


def get_authz_bundle(ctx, org_id, **kwargs):
    api = get_api(ctx)
    org_id = get_org_from_input_or_ctx(ctx, org_id=org_id)

    return api.get_authz_bundle(org_id, **strip_none(kwargs))
