import time
import click
from vijil.utils import find_job_by_task_id, format_datetime

from vijil.vijilapi.api_handler import check_jobs_progress, job_status_request, list_job_request

@click.group()
def describe():
    """[evaluation | log]"""
    pass

@describe.command()
@click.option('--id', prompt='Enter ID that you received while creating evaluation', type=str)
@click.option('--trail', is_flag=True, help='Print live logs for in-progress jobs')
def log(id, trail):
    printed_lines = set()
    try:
        joblist = list_job_request()
        matched_job = find_job_by_task_id(joblist, id)
        if matched_job:
            if matched_job.get('status') == 'In Progress':
                if trail:
                    while True:
                        live_logs = check_jobs_progress(id)
                        for log in live_logs.get('progress'):
                            if log not in printed_lines:
                                print(log)
                                printed_lines.add(log)
                        time.sleep(5)
                else:
                    print("Job is still in progress. Use --trail to get live logs.")
            else:
                result = [matched_job.get('job_result')] if matched_job.get('status') == "Stopped" else matched_job.get('output')
                for item in result:
                    print(item)
        else:
            print("No matching job found.")

    except ValueError as e:
        error_detail = str(e)
        if error_detail == "400: Job is already completed.":
            joblist = list_job_request()
            matched_job = find_job_by_task_id(joblist, id)
            result = [matched_job.job_result] if matched_job.get('status') == "Stopped" else matched_job.get('output')
            for item in result:
                if item not in printed_lines:
                    print(log)
                    printed_lines.add(log)
        else:
            click.echo(f"Error: {error_detail}")           

@describe.command()
@click.option('--id', prompt='Enter ID that you received while creating evaluation', type=str)
def evaluation(id):
    click.echo(f"Getting job status for ID: {id}")
    try:
        result = job_status_request(id)
        if "job_result" in result:
            click.echo(f"Job Status: {result.get('status')}") 
            click.echo(f"Job Result: {result.get('job_result')}")
        elif "status" in result:
            click.echo(f"Job Status: {result.get('status')}") 
        elif isinstance(result, type([])) and len(result) > 0:
            click.echo("-" * 60)
            for job in result:
                click.echo(f"Job ID: {job.get('job_id', '')}")
                click.echo(f"Model Hub: {job.get('model_type', '')}")
                click.echo(f"Model Name: {job.get('model_name', '')}")
                click.echo(f"Probe Group: {job.get('probe_group', '')}")
                click.echo("Probes:")
                for probe in job.get('probe', []):
                    click.echo(f"  - {probe}")

                click.echo("Detectors:")
                for detector in job.get('detector', []):
                    click.echo(f"  - {detector}")
                click.echo(f"Start Time: {format_datetime(job.get('start_time', ''))}")
                click.echo(f"Report: {job.get('report', '')}")
                click.echo(f"Hitlog: {job.get('hitlog', '')}")
                click.echo("-" * 60)
        else:
            click.echo("No data found.")

    except ValueError as e:
        click.echo(f"Error: {e}")
