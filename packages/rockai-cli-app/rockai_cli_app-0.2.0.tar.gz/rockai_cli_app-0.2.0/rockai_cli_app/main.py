import typer
from rockai_cli_app.server.http import start_server
from pathlib import Path
from rockai_cli_app.parser.config_util import parse_config_file
from typing_extensions import Annotated
from typing import Optional
import docker
from rockai_cli_app.docker.docker_util import build_final_image
from rich.progress import Progress, SpinnerColumn, TextColumn
import subprocess

app = typer.Typer()

APP_NAME = "rockai-cli-app"


@app.callback()
def callback():
    """
    Callback for the CLI app before any command
    """
    typer.echo("callback excuted")


@app.command()
def login():
    """
    Login using auth token
    """
    typer.echo("Login to Rock ai")


@app.command()
def init():
    file = open('rock.yaml', 'w')
    file.close()
    file = open('predict.py', 'w')
    file.close()



@app.command()
def build():
    """
    Build the image
    """
    config_path: Path = Path.cwd() / "rock.yaml"
    if not config_path.is_file():
        raise Exception("rock.yaml config file doesn't exist in the current directory")
    else:
        print("rock.yaml config file exist")
    config_map = parse_config_file(config_path)
    print(config_map)
    build_final_image(config_map=config_map)

    


@app.command()
def start(port: Annotated[int, typer.Option(help="Port of the server, default is 8000")] = 8000):
    """
    start local development server
    """
    start_server(port)
