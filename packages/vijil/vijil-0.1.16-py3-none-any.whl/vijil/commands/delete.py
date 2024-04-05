import click

from vijil.vijilapi.api_handler import delete_job_request

@click.group()
def delete():
    """[evaluation]"""
    pass

@delete.command()
@click.option('--id', prompt='Enter ID that you received while creating evaluation', type=str)
def evaluation(id):
    click.echo(f"Deleting evaluation with ID: {id}")
    try:
        result = delete_job_request(id)
        if result:
            click.echo(f"{result.get('message')}") 

    except ValueError as e:
        click.echo(f"Error: {e}")
