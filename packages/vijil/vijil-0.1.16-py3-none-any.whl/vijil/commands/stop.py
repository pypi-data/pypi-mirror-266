import click

from vijil.vijilapi.api_handler import stop_all_job_request, stop_job_request

@click.group()
def stop():
    """[evaluation]"""
    pass

@stop.command()
@click.option('--id', default='', help='Enter ID that you received while creating evaluation')
@click.option('-a', '--all', is_flag=True, help='Stop all running evaluations.')
def evaluation(id, all):
    if all:
        click.echo(f"Stopping all running evaluations.")
        try:
            result = stop_all_job_request()
            if result.get("status"):
                click.echo(f"Job Status: {result.get('status')}") 
        except ValueError as e:
            click.echo(f"Error: {e}")
    else:
        if not id:
            click.echo("Please provide the ID for stopping a specific job.")
            return
        click.echo(f"Stopping evaluation of ID: {id}")
        try:
            result = stop_job_request(id)
            if result.get("status"):
                click.echo(f"Job Status: {result.get('status')}") 
        except ValueError as e:
            click.echo(f"Error: {e}")
