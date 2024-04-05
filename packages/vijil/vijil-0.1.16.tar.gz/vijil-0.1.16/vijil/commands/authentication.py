import click
import requests
from vijil.vijilapi.api_handler import VIGIL_API_BASE_URL
from vijil.vijilapi.config_handler import remove_config, save_config

@click.argument('username')
@click.option('--token', prompt='Enter your token', hide_input=True)
@click.command()
def login(username, token):
    """[username]"""
    click.echo(f"Verifying your credentials...")
    verify_url = f"{VIGIL_API_BASE_URL}/tokens/verify"
    data = {"username": username, "token": token}

    try:
        response = requests.post(verify_url, json=data)
        response.raise_for_status()

        if response.json().get("verify"):
            save_config(username, token)
            click.echo("Token verified.")
        else:
            click.echo("Token verification failed. Please try a different token.")

    except requests.exceptions.RequestException as e:
        click.echo(f"Error during API request: {e}")

@click.command()
def logout():
    remove_config()
    click.echo("Logout done")
