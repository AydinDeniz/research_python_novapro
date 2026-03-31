# Prompt 86

import subprocess
import typer

app = typer.Typer()

@app.command()
def list_containers():
    result = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True)
    print(result.stdout)

@app.command()
def start_container(container_id: str):
    result = subprocess.run(["docker", "start", container_id], capture_output=True, text=True)
    print(result.stdout)

@app.command()
def stop_container(container_id: str):
    result = subprocess.run(["docker", "stop", container_id], capture_output=True, text=True)
    print(result.stdout)

@app.command()
def remove_container(container_id: str):
    result = subprocess.run(["docker", "rm", container_id], capture_output=True, text=True)
    print(result.stdout)

if __name__ == "__main__":
    app()