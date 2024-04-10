import click
from hcs_core.sglib import cli_options as cli
from hcs_cli.service import admin


@click.command()
@click.option("--template", "-t", required=False)
@click.option("--vm", required=False)
@cli.org_id
def dump(org: str, template: str):
    org_id = cli.get_org_id(org)
    if template:
        t = admin.template.get(template, org_id)
        if t:
            templates = [t]
    else:
        templates = admin.template.list(org_id)

    return templates
