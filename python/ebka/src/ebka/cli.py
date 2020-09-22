import click   # For pylance errors

@click.group()
@click.pass_context
def cli(summary):
    pass

@cli.command()
def hello():
    click.echo("Hello")

@cli.command()
def bye():
    click.echo("Goodbye")

if __name__=="__main__":
    cli()