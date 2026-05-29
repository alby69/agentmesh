import typer
from rich.console import Console

app = typer.Typer(help="AgentMesh Studio: Developer tools for the Coordination Mesh")
console = Console()

@app.command()
def info():
    """Display information about the AgentMesh workspace."""
    console.print("[bold blue]AgentMesh Studio[/bold blue]")
    console.print("Version: 0.1.0")
    console.print("\n[yellow]Active Apps:[/yellow]")
    console.print("- podcast-generator")
    console.print("- motedico (placeholder)")
    console.print("\n[yellow]Core Packages:[/yellow]")
    console.print("- agentmesh-core")
    console.print("- agentmesh-relay")
    console.print("- agentmesh-vault")

@app.command()
def vision():
    """Display the AgentMesh vision."""
    console.print("[bold green]Coordination Mesh Vision[/bold green]")
    console.print("A decentralized network of cooperative agents and knowledge.")
    console.print("Built on Nostr (Communication) and IPFS (Storage).")

if __name__ == "__main__":
    app()
