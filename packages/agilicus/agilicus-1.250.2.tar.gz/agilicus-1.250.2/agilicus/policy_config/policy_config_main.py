import click
from ..output.table import output_entry
from . import policy_config


@click.command(name="get-authz-bundle")
@click.pass_context
@click.option("--org-id", default=None)
@click.option("--policy-config-etag", default=None)
def cli_command_get_authz_bundle(ctx, **kwargs):
    result = policy_config.get_authz_bundle(ctx, **kwargs)
    output_entry(ctx, result.to_dict())


all_funcs = [func for func in dir() if "cli_command_" in func]


def add_commands(cli):
    glob = globals()
    for func in all_funcs:
        cli.add_command(glob[func])
