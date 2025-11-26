#!/usr/bin/env python3
"""
AI-Powered CV Automation System
Tailors LaTeX CV based on job postings using GPT-4o-mini
"""
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
from typing import Optional

from src.config_manager import ConfigManager
from src.job_analyzer import JobAnalyzer
from src.cv_generator import CVGenerator
from src.logger import setup_logger
from src.utils import (
    validate_job_posting,
    read_file,
    sanitize_filename,
    format_confidence,
    ensure_directory
)

# Initialize logger
logger = setup_logger("cv_automation", "INFO")

app = typer.Typer(help="AI-Powered CV Automation System")
console = Console()


def initialize_system():
    """Initialize configuration and components."""
    try:
        logger.info("Initializing CV automation system...")
        config = ConfigManager()
        logger.info("ConfigManager initialized")
        analyzer = JobAnalyzer(config)
        logger.info("JobAnalyzer initialized")
        generator = CVGenerator(config)
        logger.info("CVGenerator initialized")
        logger.info("System initialization complete")
        return config, analyzer, generator
    except Exception as e:
        logger.error(f"Error initializing system: {e}", exc_info=True)
        console.print(f"[red]Error initializing system: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def setup():
    """Create necessary directories and sample files."""
    console.print("[yellow]Setting up CV automation system...[/yellow]")

    # Create directories
    directories = ['output', 'tests/sample_jobs', 'config']
    for directory in directories:
        ensure_directory(directory)
        console.print(f"Created directory: {directory}")

    # Create sample job posting
    sample_job = Path("tests/sample_jobs/sample_job.txt")
    if not sample_job.exists():
        sample_content = """Senior Software Engineer - AWS Infrastructure

We are seeking an experienced Senior Software Engineer to join our cloud infrastructure team.
You will work on large-scale distributed systems and microservices architecture.

Requirements:
- 5+ years of experience with Python and backend development
- Strong expertise in AWS (EC2, S3, Lambda, CloudFormation)
- Experience with Docker and Kubernetes
- Knowledge of microservices architecture and distributed systems
- Experience with CI/CD pipelines

This is a great opportunity to work on high-scale systems at a leading tech company.
"""
        sample_job.write_text(sample_content)
        console.print(f"Created sample job posting: {sample_job}")

    console.print("[green]Setup complete![/green]")


@app.command()
def test_api():
    """Test OpenAI API connection."""
    console.print("[yellow]Testing OpenAI API connection...[/yellow]")

    try:
        config, analyzer, _ = initialize_system()

        if analyzer.test_connection():
            console.print("[green]API connection successful![/green]")
            console.print(f"[dim]Using model: {analyzer.model}[/dim]")
            console.print("[dim]Estimated cost per analysis: ~$0.002[/dim]")
        else:
            console.print("[red]API connection failed![/red]")
            raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        console.print("[yellow]Make sure OPENAI_API_KEY is set in .env file[/yellow]")
        raise typer.Exit(1)


@app.command()
def generate(
    job: str = typer.Option(..., help="Path to job posting text file"),
    output: Optional[str] = typer.Option(None, help="Custom output filename (without .pdf)"),
    auto: bool = typer.Option(False, "--auto", "-a", help="Auto-accept AI recommendation"),
):
    """Generate tailored CV from job posting."""

    # Validate input file
    if not validate_job_posting(job):
        console.print(f"[red]Error: Job posting file not found or empty: {job}[/red]")
        raise typer.Exit(1)

    # Initialize system
    config, analyzer, generator = initialize_system()

    # Read job posting
    console.print(f"[cyan]Reading job posting: {job}[/cyan]")
    job_text = read_file(job)

    # Analyze with AI
    console.print("[yellow]Analyzing job posting with AI...[/yellow]")
    try:
        analysis = analyzer.analyze_job_posting(job_text)
    except Exception as e:
        console.print(f"[red]Error analyzing job posting: {e}[/red]")
        raise typer.Exit(1)

    # Display results
    console.print(Panel.fit(
        f"[bold green]Job Analysis Complete[/bold green]\n\n"
        f"[cyan]Role:[/cyan] {analysis['role']}\n"
        f"[cyan]Keywords found:[/cyan] {len(analysis['keywords'])}\n"
        f"[cyan]AI Recommendation:[/cyan] {analysis['version']} "
        f"(Confidence: {format_confidence(analysis['confidence'])})",
        title="Analysis Results"
    ))

    # Show available versions
    if not auto:
        table = Table(title="Available CV Versions")
        table.add_column("#", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Description", style="white")

        versions = config.get_all_versions()
        version_list = list(versions.keys())

        for i, (version_key, version_data) in enumerate(versions.items(), 1):
            marker = "[bold yellow]*[/bold yellow]" if version_key == analysis['version'] else ""
            table.add_row(
                str(i),
                f"{version_key} {marker}",
                version_data['description']
            )

        console.print(table)
        console.print("[dim]* = AI Recommendation[/dim]")

        # User selection
        choice = typer.prompt(
            "Select version [1/2/3/4/ai]",
            default="ai"
        )

        if choice == "ai":
            selected_version = analysis['version']
        else:
            try:
                idx = int(choice) - 1
                selected_version = version_list[idx]
            except (ValueError, IndexError):
                console.print("[red]Invalid choice. Using AI recommendation.[/red]")
                selected_version = analysis['version']

        analysis['version'] = selected_version

    console.print(f"[green]Using version: {analysis['version']}[/green]")

    # Update CV files
    console.print("[yellow]Updating CV files...[/yellow]")

    if generator.generate_cv(analysis):
        console.print(f"   [green]Header title updated:[/green] {analysis['role']}")
        console.print("   [green]ATS boost updated[/green] with job keywords")
        console.print(f"   [green]Version flags updated:[/green] {analysis['version']} activated")
    else:
        console.print("[red]Error updating CV files[/red]")
        raise typer.Exit(1)

    # Compile PDF
    console.print("[yellow]Compiling PDF...[/yellow]")

    # Generate output filename
    if not output:
        output = sanitize_filename(analysis['role'])  # Remove _{analysis['version'].lower()}

    if generator.compile_pdf(output):
        console.print(f"[bold green]Success! CV generated:[/bold green] output/{output}.pdf")

        # Show summary
        summary = Panel.fit(
            f"[bold]CV Generation Summary[/bold]\n\n"
            f"[cyan]Job Title:[/cyan] {analysis['role']}\n"
            f"[cyan]CV Version:[/cyan] {analysis['version']}\n"
            f"[cyan]Keywords:[/cyan] {len(analysis['keywords'])}\n"
            f"[cyan]Output:[/cyan] output/{output}.pdf\n"
            f"[cyan]ATS Optimized:[/cyan] Yes",
            title="Complete",
            border_style="green"
        )
        console.print(summary)

        # Cleanup
        generator.cleanup_latex_artifacts()

    else:
        console.print("[red]Error compiling PDF[/red]")
        raise typer.Exit(1)


@app.command()
def test():
    """Run test suite with sample job postings."""
    console.print("[yellow]Running test suite...[/yellow]")

    sample_jobs_dir = Path("tests/sample_jobs")

    if not sample_jobs_dir.exists():
        console.print("[red]Sample jobs directory not found. Run 'python main.py setup' first.[/red]")
        raise typer.Exit(1)

    sample_files = list(sample_jobs_dir.glob("*.txt"))

    if not sample_files:
        console.print("[red]No sample job files found in tests/sample_jobs/[/red]")
        raise typer.Exit(1)

    console.print(f"Found {len(sample_files)} sample job posting(s)")

    config, analyzer, generator = initialize_system()

    for job_file in sample_files:
        console.print(f"\n[cyan]Testing: {job_file.name}[/cyan]")
        job_text = read_file(str(job_file))

        try:
            analysis = analyzer.analyze_job_posting(job_text)
            console.print(f"  Role: {analysis['role']}")
            console.print(f"  Version: {analysis['version']} ({format_confidence(analysis['confidence'])})")
            console.print(f"  Keywords: {len(analysis['keywords'])}")
            console.print("[green]  PASSED[/green]")
        except Exception as e:
            console.print(f"[red]  FAILED: {e}[/red]")

    console.print("\n[green]Test suite complete![/green]")


@app.command()
def info():
    """Show system information and configuration."""
    config, _, _ = initialize_system()

    console.print(Panel.fit(
        "[bold]CV Automation System Info[/bold]\n\n"
        "[cyan]Version:[/cyan] 1.0.0\n"
        "[cyan]Model:[/cyan] GPT-4o-mini\n"
        "[cyan]Cost per analysis:[/cyan] ~$0.002\n"
        "[cyan]LaTeX Engine:[/cyan] pdflatex (MiKTeX)",
        title="System Information"
    ))

    # Show available versions
    table = Table(title="CV Versions")
    table.add_column("Version", style="green")
    table.add_column("Description", style="white")
    table.add_column("Keywords", style="cyan")

    versions = config.get_all_versions()
    for version_key, version_data in versions.items():
        keywords = config.get_version_keywords(version_key)
        keywords_str = ", ".join(keywords[:5]) + "..."
        table.add_row(version_key, version_data['description'], keywords_str)

    console.print(table)


if __name__ == "__main__":
    app()
