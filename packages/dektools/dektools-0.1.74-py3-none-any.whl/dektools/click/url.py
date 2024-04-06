import sys
import typer
from ..url import get_auth_url

app = typer.Typer(add_completion=False)


@app.command()
def auth(url, username, password=None):
    sys.stdout.write(get_auth_url(url, username, password))
