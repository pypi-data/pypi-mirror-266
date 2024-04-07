import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def viewtensor(filepath: str):
    from dstool.tensors.safetensors import (
        get_tensor_stats,
        tensorstats_to_table
    )
    stats = get_tensor_stats(filepath)
    table = tensorstats_to_table(filepath, stats)
    console.print(table)
    
@app.command()
def version():
    print("0.1.0")

if __name__ == "__main__":  # pragma: no cover
    app()