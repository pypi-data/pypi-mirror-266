import click
from vijil.commands.authentication import login, logout
from vijil.commands.create import create
from vijil.commands.describe import describe
from vijil.commands.download import download
from vijil.commands.start import start
from vijil.commands.stop import stop
from vijil.commands.delete import delete
from vijil.commands.list import list

@click.group()
def main():
    """VIJIL Command Line Interface"""

main.add_command(login)
main.add_command(logout)
main.add_command(start)
main.add_command(stop)
main.add_command(describe)
main.add_command(delete)
main.add_command(download)
main.add_command(list)
main.add_command(create)

if __name__ == '__main__':
    main()
