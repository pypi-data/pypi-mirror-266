import click

from tabulate import tabulate
from vijil.utils import format_datetime, get_dimensions_from_probe_groups
from vijil.vijilapi.api_handler import get_model_token_request, list_job_request

@click.group()
def list():
    """[evaluations | tokens]"""
    pass

@list.command()
def tokens():
    try:
        result = get_model_token_request()
        if len(result) > 0:
            table_data = []
            for token in result:
                table_data.append([
                    token.get('name', ''),
                    token.get('type', ''),
                    token.get('token', ''),
                    token.get('isPrimary', '')
                ])

            headers = ["Name", "Type", "Token", "isDefault"]
            colalign = ['left'] * len(headers)
            tablefmt = "heavy_grid"
            maxcolwidths = [None, None, 50, None]

            table = tabulate(table_data, headers=headers, tablefmt=tablefmt, colalign=colalign, maxcolwidths=maxcolwidths)
            click.echo(table)
        else:
            click.echo("No tokens found.")

    except ValueError as e:
        click.echo(f"Error: {e}")

@list.command
def evaluations():
    try:
        result = list_job_request()
        if len(result) > 0:
            table_data = []
            for job in result:
                probe_groups_list = job.get('probe_group', '').split(",")
                table_data.append([
                    job.get('id', ''),
                    job.get('model_type', ''),
                    job.get('model_name', ''),
                    "\n".join(get_dimensions_from_probe_groups(probe_groups_list)),
                    "\n".join(probe_groups_list),
                    job.get('status', ''),
                    job.get('job_result', ''),
                    format_datetime(job.get('start_time', '')),
                    format_datetime(job.get('end_time', ''))
                ])

            headers = ["ID", "Model Hub", "Model Name", "Dimension", "Probe Group", "Status", "Output", "Start Time", "End Time"]
            maxcolwidths = [None, 10, 25, None, None, None, 30, None, None]

            colalign = ['left'] * len(headers)
            tablefmt = "heavy_grid"
            table = tabulate(table_data, headers=headers, tablefmt=tablefmt, colalign=colalign, maxcolwidths=maxcolwidths)
            click.echo(table)
        else:
            click.echo("No jobs found.")

    except ValueError as e:
        click.echo(f"Error: {e}")
