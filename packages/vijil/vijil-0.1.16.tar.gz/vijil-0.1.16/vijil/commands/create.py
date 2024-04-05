import click
from vijil.evaluations.options import MODEL_HUB_CHOICES, MODEL_TYPE_MAPPING
from vijil.vijilapi.api_handler import model_token_request

@click.group()
def create():
    """[token]"""
    pass

@create.command()
@click.argument('source', type=click.Choice(MODEL_HUB_CHOICES))
@click.option('--name', prompt='Enter the name of token')
@click.option('--token', prompt='Enter the token')
@click.option('--is-primary', prompt='Do you want to make this token as the default?', type=click.Choice(['yes', 'no']))
def token(source, name, token, is_primary):
    isPrimary = "true" if is_primary == 'yes' else "false"
    try:
        result = model_token_request(MODEL_TYPE_MAPPING.get(source), name, token, isPrimary)
        if result:
            click.echo(f"Successfully saved integration token.")

    except ValueError as e:
        click.echo(f"Error: {e}")
