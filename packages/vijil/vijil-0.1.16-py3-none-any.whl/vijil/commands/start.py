import click

from vijil.evaluations.options import DTYPE_CHOICES, MODEL_HUB_CHOICES, PROBES_CHOICES, PROBES_DIMENSIONS_MAPPING
from vijil.utils import generate_default_job_name
from vijil.vijilapi.api_handler import get_headers, list_job_request, send_evaluation_request

@click.group()
def start():
    """[evaluation]"""
    pass

@start.command()
@click.option('--model-hub', prompt='Choose the model hub', type=click.Choice(MODEL_HUB_CHOICES))
@click.option('--model-name', prompt='Enter the model name')
@click.option('--dimension', prompt='Choose the trust dimension', type=click.Choice(PROBES_CHOICES))
@click.option('--deployment-type', prompt='Choose the deployment type', type=click.Choice(DTYPE_CHOICES))
@click.option('--generations', default=1, prompt='Enter the number of generations', type=click.IntRange(1, 100))
@click.option('--token', default='', prompt='Enter the model token')
def evaluation(model_hub, model_name, dimension, deployment_type, generations, token):
    try:
        headers = get_headers()
        if model_hub != 'huggingface' and deployment_type == 'local':
            click.echo(f"Local deployment type is not allowed for model {model_hub}.")
            return
        
        # probes = PROBES_DIMENSIONS_MAPPING.get(dimension)

        click.echo(f"Running evaluation for model hub: {model_hub}, model name: {model_name}")
        
        job_name = generate_default_job_name(headers['username'], model_hub, model_name)
        result = send_evaluation_request(model_hub, model_name, dimension, generations, job_name, deployment_type, token)

        
        if result.get("task_id"):
            click.echo(f"Successfully created evaluation, check job status by ID: {result.get('task_id')}")    
        else:
            click.echo(f"Response: {result}")

    except ValueError as e:
        click.echo(f"Error: {e}")
