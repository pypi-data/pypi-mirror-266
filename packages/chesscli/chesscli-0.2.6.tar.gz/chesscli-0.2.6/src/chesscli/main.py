import typer
import subprocess
from pathlib import Path
import shlex
from typing import Optional

app = typer.Typer()

default_config_path = Path.home() / ".chess_cli_config"


def get_repo_path_from_config() -> Path:
    try:
        with open(default_config_path, 'r') as f:
            return Path(f.read().strip())
    except FileNotFoundError:
        typer.echo("Configuration file not found, please run the configure command first.")
        raise typer.Exit()

@app.command()
def configure():
    repo_path = typer.prompt("Where is your repo cloned?")
    with open("chess_cli_config.txt", 'w') as f:
        f.write(repo_path)
    typer.echo("Repo path configured!")

@app.command()
def code():
    repo_path = get_repo_path_from_config()
    subprocess.run(shlex.split(f"code {repo_path.as_posix()}"), check=True, shell=True)
    typer.echo("Opening Visual Studio Code.")

@app.command()
def start():
    repo_path = get_repo_path_from_config()
    subprocess.run(["docker-compose", "up", "--build"], cwd=repo_path.as_posix(), check=True)
    typer.echo("Docker containers started.")

@app.command()
def stop():
    repo_path = get_repo_path_from_config()
    subprocess.run(["docker-compose", "down"], cwd=repo_path.as_posix(), check=True)
    typer.echo("Docker containers stopped.")
    
    
@app.command()
def test():
    repo_path = get_repo_path_from_config()
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'], cwd=(repo_path / 'backend').as_posix(), check=True)
    subprocess.run(['python', '-m', 'pytest', 'tests/'], cwd=(repo_path / 'backend').as_posix(), check=True)
    typer.echo("Running Tests..")
    

@app.command()
def setup():
    default_repo_url = "https://github.com/neelthepatel8/chessgame"
    default_clone_folder = Path.home() / "dev/proj/chess/game"
    
    repo_url = typer.prompt("Enter the repository URL to clone", default=default_repo_url)
    clone_folder = typer.prompt("Enter the folder to clone the repo into", default=str(default_clone_folder))
    clone_path = Path(clone_folder)
    
    if not clone_path.exists():
        typer.echo(f"Creating folder {clone_path}")
        clone_path.mkdir(parents=True, exist_ok=True)

    typer.echo("Cloning the repository...")
    try:
        subprocess.check_output(shlex.split(f"git clone {repo_url} {clone_path.as_posix()}"), stderr=subprocess.STDOUT,  shell=True)
    except subprocess.CalledProcessError as e:
        print("Error cloning repository:  rc=", e.returncode, "output=", e.output)
        return 
    
    with open(default_config_path, 'w') as f:
        f.write(str(clone_path))
    typer.echo("Repository cloned and configuration saved.")
    
    typer.echo("\nYou can now run the following commands:")
    typer.echo("1. code: Opens the cloned repository in Visual Studio Code.")
    typer.echo("2. start: Starts the Docker containers.")
    typer.echo("3. stop: Stops the Docker containers.")
    typer.echo("Remember to run 'configure' if the repository path changes.")

if __name__ == "__main__":
    app()
