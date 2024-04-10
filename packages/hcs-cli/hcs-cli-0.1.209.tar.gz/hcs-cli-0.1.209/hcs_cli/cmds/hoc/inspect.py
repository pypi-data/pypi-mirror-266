import click
import hcs_ext_hoc as hoc


@click.command()
@click.option("--org", required=True)
@click.option("--template", "-t", required=False)
@click.option("--vm", required=False)
def inspect(org: str, template: str, vm: str):
    return hoc.inspect(org, template, vm)
