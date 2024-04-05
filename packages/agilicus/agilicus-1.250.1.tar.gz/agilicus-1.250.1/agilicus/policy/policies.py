from ..input_helpers import (
    get_org_from_input_or_ctx,
    strip_none,
)

from .. import context

from agilicus import (
    create_or_update,
    LabelName,
    PolicyTemplateInstance,
    PolicyTemplateInstanceSpec,
    MFAPolicyTemplate,
)

from ..output.table import (
    format_table,
    spec_column,
    metadata_column,
    subtable,
    column,
)


class InstanceAddInfo:
    def __init__(self, apiclient):
        super().__init__()


def set_multifactor_policy(ctx, name, duration, label=None, description=None, **kwargs):
    org_id = get_org_from_input_or_ctx(ctx, **kwargs)

    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    mfa = MFAPolicyTemplate(
        seconds_since_last_challenge=duration,
        labels=[LabelName(la) for la in (label or [])],
        template_type="mfa",
    )

    spec = PolicyTemplateInstanceSpec(
        org_id=org_id,
        name=name,
        template=mfa,
    )

    if description is not None:
        spec.description = description

    tmpl = PolicyTemplateInstance(spec=spec)
    templates_api = apiclient.policy_templates_api
    resp, _ = create_or_update(
        tmpl,
        lambda obj: templates_api.create_policy_template_instance(obj),
        lambda guid, obj: templates_api.replace_policy_template_instance(
            guid, policy_template_instance=obj
        ),
        to_dict=False,
    )
    return resp


def ruleset_labelled(ruleset, label):
    for ruleset_label in ruleset.spec.labels or []:
        if str(ruleset_label) == label:
            return True
    return False


def list_multifactor_policies(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    result = apiclient.policy_templates_api.list_policy_template_instances(
        org_id=org_id, template_type="mfa"
    )
    return result.policy_template_instances


def format_multifactor_policies(ctx, templates):
    mfa_columns = [
        column("seconds_since_last_challenge"),
        column("labels"),
    ]
    mfa_table = subtable(ctx, "spec.template", mfa_columns)
    columns = [
        spec_column("org_id"),
        spec_column("name"),
        spec_column("template.template_type", "type"),
        mfa_table,
    ]

    return format_table(ctx, templates, columns)


def list_policy_templates(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    kwargs["org_id"] = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs = strip_none(kwargs)
    result = apiclient.policy_templates_api.list_policy_template_instances(**kwargs)
    return result.policy_template_instances


def delete_policy_template(ctx, instance_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    kwargs["org_id"] = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs = strip_none(kwargs)
    apiclient.policy_templates_api.delete_policy_template_instance(instance_id, **kwargs)


def get_policy_template(ctx, instance_id, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    kwargs["org_id"] = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs = strip_none(kwargs)
    return apiclient.policy_templates_api.get_policy_template_instance(
        instance_id, **kwargs
    )


def format_policy_templates(ctx, templates):
    columns = [
        spec_column("org_id"),
        metadata_column("id"),
        spec_column("name"),
        spec_column("template.template_type", "type"),
        spec_column("description"),
        spec_column("template"),
    ]

    return format_table(ctx, templates, columns)
