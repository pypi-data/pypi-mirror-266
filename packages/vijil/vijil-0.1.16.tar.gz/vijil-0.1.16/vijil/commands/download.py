import click

from vijil.vijilapi.api_handler import download_report_request, job_status_request

@click.group()
def download():
    """[log]"""
    pass

@download.command()
@click.argument("report_type", type=click.Choice(["full", "failure"]))
@click.option('--id', prompt='Enter ID that you received while creating evaluation', type=str)
def log(report_type, id):
    """[full | failure]"""
    try:
        result = job_status_request(id)
        if isinstance(result, type([])) and len(result) > 0:
            file_id = result[0].get("report" if report_type == "full" else "hitlog")
            result = download_report_request(file_id)
            if result:
                click.echo(f"{result}")
            else:
                click.echo("No data found.")
        else:
            click.echo("No data found")

    except ValueError as e:
        click.echo(f"Error: {e}")
