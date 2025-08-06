"""
Command-line interface for PySeesAbq.

This module provides the CLI for converting Abaqus files to OpenSeesPy format.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import track
from rich.table import Table
from rich import print as rprint

from . import __version__
from .core import convert_file
from .parser import AbaqusParser


console = Console()


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    """
    PySeesAbq - Convert Abaqus .inp files to OpenSeesPy Python scripts.
    
    INTERNAL COMPANY TOOL - CONFIDENTIAL AND PROPRIETARY
    For internal use only. Unauthorized distribution prohibited.
    """
    if version:
        from . import __version__, __copyright__
        click.echo(f"PySeesAbq {__version__}")
        click.echo(__copyright__)
        click.echo("Internal Company Tool - Proprietary Software")
        return
    
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('-o', '--output', 'output_file', type=click.Path(path_type=Path),
              help='Output Python file path (default: input_file.py)')
@click.option('--overwrite', is_flag=True,
              help='Overwrite output file if it exists')
@click.option('-v', '--verbose', is_flag=True,
              help='Enable verbose output')
@click.option('--dry-run', is_flag=True,
              help='Parse file and show statistics without converting')
def convert(
    input_file: Path,
    output_file: Optional[Path],
    overwrite: bool,
    verbose: bool,
    dry_run: bool
) -> None:
    """
    Convert an Abaqus .inp file to OpenSeesPy Python script.
    
    INPUT_FILE: Path to the Abaqus .inp file to convert
    """
    try:
        if dry_run:
            _dry_run_analysis(input_file, verbose)
            return
            
        if verbose:
            rprint(f"[bold blue]Converting:[/bold blue] {input_file}")
            
        with console.status("[bold green]Converting...") as status:
            output_path = convert_file(
                input_file=input_file,
                output_file=output_file,
                overwrite=overwrite,
                verbose=verbose
            )
            
        rprint(f"[bold green]✓ Conversion completed![/bold green]")
        rprint(f"[bold]Output:[/bold] {output_path}")
        
    except FileNotFoundError as e:
        rprint(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except FileExistsError as e:
        rprint(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except ValueError as e:
        rprint(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        rprint(f"[bold red]Unexpected error:[/bold red] {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose output')
def info(input_file: Path, verbose: bool) -> None:
    """
    Show information about an Abaqus .inp file.
    
    INPUT_FILE: Path to the Abaqus .inp file to analyze
    """
    try:
        _dry_run_analysis(input_file, verbose, show_details=True)
    except Exception as e:
        rprint(f"[bold red]Error analyzing file:[/bold red] {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('-o', '--output-dir', type=click.Path(path_type=Path),
              help='Output directory (default: same as input directory)')
@click.option('--overwrite', is_flag=True,
              help='Overwrite output files if they exist')
@click.option('-v', '--verbose', is_flag=True,
              help='Enable verbose output')
def batch(
    directory: Path,
    output_dir: Optional[Path],
    overwrite: bool,
    verbose: bool
) -> None:
    """
    Convert all .inp files in a directory to OpenSeesPy scripts.
    
    DIRECTORY: Path to directory containing .inp files
    """
    try:
        inp_files = list(directory.glob("*.inp"))
        
        if not inp_files:
            rprint(f"[yellow]No .inp files found in {directory}[/yellow]")
            return
            
        if output_dir is None:
            output_dir = directory
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
            
        rprint(f"[bold blue]Found {len(inp_files)} .inp files[/bold blue]")
        
        successful = 0
        failed = 0
        
        for inp_file in track(inp_files, description="Converting files..."):
            try:
                output_file = output_dir / inp_file.with_suffix('.py').name
                convert_file(
                    input_file=inp_file,
                    output_file=output_file,
                    overwrite=overwrite,
                    verbose=False
                )
                successful += 1
                if verbose:
                    rprint(f"[green]✓[/green] {inp_file.name}")
            except Exception as e:
                failed += 1
                rprint(f"[red]✗[/red] {inp_file.name}: {e}")
                
        rprint(f"\n[bold]Results:[/bold]")
        rprint(f"[green]Successful: {successful}[/green]")
        if failed > 0:
            rprint(f"[red]Failed: {failed}[/red]")
            
    except Exception as e:
        rprint(f"[bold red]Error during batch conversion:[/bold red] {e}")
        sys.exit(1)


def _dry_run_analysis(input_file: Path, verbose: bool, show_details: bool = False) -> None:
    """Perform dry run analysis of an Abaqus file."""
    rprint(f"[bold blue]Analyzing:[/bold blue] {input_file}")
    
    with console.status("[bold green]Parsing..."):
        parser = AbaqusParser()
        parsed_data = parser.parse(str(input_file))
    
    # Create summary table
    table = Table(title=f"Analysis Summary: {input_file.name}")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Count", style="magenta", justify="right")
    
    table.add_row("Nodes", str(len(parsed_data.nodes)))
    table.add_row("Elements", str(len(parsed_data.elements)))
    table.add_row("Materials", str(len(parsed_data.materials)))
    table.add_row("Sections", str(len(parsed_data.sections)))
    table.add_row("Boundary Conditions", str(len(parsed_data.boundaries)))
    table.add_row("Loads", str(len(parsed_data.loads)))
    table.add_row("Element Sets", str(len(parsed_data.element_sets)))
    table.add_row("Node Sets", str(len(parsed_data.node_sets)))
    
    console.print(table)
    
    if show_details and verbose:
        # Show element types
        if parsed_data.elements:
            element_types = {}
            for elem_data in parsed_data.elements.values():
                elem_type = elem_data.get('type', 'Unknown')
                element_types[elem_type] = element_types.get(elem_type, 0) + 1
            
            rprint("\n[bold]Element Types:[/bold]")
            for elem_type, count in element_types.items():
                rprint(f"  {elem_type}: {count}")
        
        # Show materials
        if parsed_data.materials:
            rprint("\n[bold]Materials:[/bold]")
            for material_name in parsed_data.materials.keys():
                rprint(f"  {material_name}")


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
