"""ParseDoc CLI (Typer + Rich) - PRD #9"""

import os
from pathlib import Path

import rich
import typer
from rich.console import Console
from rich.table import Table

from .core.config import Config
from .core.detection import detect_format
from .core.pipeline import Pipeline
from .parsers import get_parser
from .utils.logging import setup_logging

app = typer.Typer(help="ParseDoc - Document → AI → Markdown")
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """ParseDoc - convert documents into clean, AI-ready Markdown."""
    if ctx.invoked_subcommand is None:
        show_header()
        console.print(
            "[yellow]Run a command, e.g.[/yellow] "
            "[bold]parsedoc convert <file> -o out.md[/bold]  "
            "(see [bold]parsedoc --help[/bold])"
        )


_BANNER = r"""
 ____                     ____
|  _ \ __ _ _ __ ___  ___|  _ \  ___   ___
| |_) / _` | '__/ __|/ _ \ | | |/ _ \ / __|
|  __/ (_| | |  \__ \  __/ |_| | (_) | (__
|_|   \__,_|_|  |___/\___|____/ \___/ \___|
"""


def _pkg_version() -> str:
    try:
        from importlib.metadata import version as _v

        return _v("docpilot-ai")
    except Exception:
        return "0.2.4"


def show_header():
    rich.print(f"[bold cyan]{_BANNER}[/bold cyan]")
    rich.print("[bold blue]ParseDoc[/bold blue] [dim]- developed by Anuj Paroha[/dim]")
    rich.print("Document → AI → Markdown")
    rich.print(f"Version {_pkg_version()}")
    rich.print()


def show_summary(metrics: dict):
    table = Table(title="Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    for k, v in metrics.items():
        table.add_row(str(k), str(v))
    console.print(table)


@app.command()
def convert(
    input_file: str = typer.Argument(..., help="Input document file"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option(
        "markdown", "--format", "-f", help="Output format (markdown, json, html, text)"
    ),
    mode: str = typer.Option("hybrid", "--mode", "-m", help="Processing mode (local, ai, hybrid)"),
    ai_provider: str = typer.Option(None, "--ai-provider", help="AI provider to use"),
    model: str = typer.Option(None, "--model", help="AI model to use"),
    temperature: float = typer.Option(0.2, "--temperature", help="Sampling temperature"),
    max_tokens: int = typer.Option(2048, "--max-tokens", help="Maximum tokens for AI"),
    ocr: bool = typer.Option(False, "--ocr", help="Force OCR processing"),
    extract_images: bool = typer.Option(
        False, "--extract-images", help="Extract embedded images into an assets folder"
    ),
    quiet: bool = typer.Option(False, "--quiet", help="Quiet mode"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose mode"),
):
    """Convert a document to structured Markdown."""
    show_header()
    if not os.path.exists(input_file):
        typer.echo(f"Error: Input file '{input_file}' not found")
        raise typer.Exit(code=1)

    setup_logging(verbose, quiet)
    config = Config().load_from_file()
    pipeline = Pipeline(config)

    try:
        result = pipeline.process(
            input_file,
            output_format=format,
            mode=mode,
            ai_provider=ai_provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            ocr=ocr,
            extract_images=extract_images,
            output_path=output,
        )
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)

    if output:
        Path(output).write_text(result, encoding="utf-8")
        typer.echo(f"✓ Created: {output}")
    else:
        typer.echo(result)

    show_summary(
        {
            "input_file": input_file,
            "output_format": format,
            "processing_mode": mode,
            "status": "success",
        }
    )


@app.command()
def batch(
    directory: str = typer.Argument(..., help="Directory containing documents"),
    pattern: str = typer.Option("*.*", "--pattern", "-p", help="File pattern to match"),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format"),
    mode: str = typer.Option("hybrid", "--mode", "-m", help="Processing mode"),
    ai_provider: str = typer.Option(None, "--ai-provider", help="AI provider"),
    model: str = typer.Option(None, "--model", help="AI model"),
    ocr: bool = typer.Option(False, "--ocr", help="Force OCR"),
    extract_images: bool = typer.Option(
        False, "--extract-images", help="Extract embedded images into an assets folder"
    ),
    output: str = typer.Option(
        "batch_out",
        "--output",
        "-o",
        help="Output directory for converted files (created in the current directory)",
    ),
):
    """Batch process multiple documents in a directory."""
    show_header()
    if not os.path.isdir(directory):
        typer.echo(f"Error: Directory '{directory}' not found")
        raise typer.Exit(code=1)

    if output:
        os.makedirs(output, exist_ok=True)

    config = Config().load_from_file()
    pipeline = Pipeline(config)
    results = pipeline.process_batch(
        directory,
        pattern,
        output_format=format,
        mode=mode,
        ai_provider=ai_provider,
        model=model,
        ocr=ocr,
        extract_images=extract_images,
    )
    ext = {"markdown": "md", "json": "json", "html": "html", "text": "txt"}.get(format, "md")
    for path, content in results.items():
        if content.startswith("ERROR:"):
            typer.echo(f"✗ {path}: {content}")
            continue
        typer.echo(f"✓ Processed: {path}")
        if output:
            out_path = os.path.join(output, f"{Path(path).stem}.{ext}")
            Path(out_path).write_text(content, encoding="utf-8")
            typer.echo(f"  → {out_path}")
    typer.echo("Batch processing completed")


@app.command()
def inspect(
    input_file: str = typer.Argument(..., help="Inspect a document file"),
    format: str = typer.Option("json", "--format", "-f", help="Inspection format (json, summary)"),
):
    """Inspect a document file structure."""
    show_header()
    if not os.path.exists(input_file):
        typer.echo(f"Error: Input file '{input_file}' not found")
        raise typer.Exit(code=1)

    config = Config().load_from_file()
    fmt = detect_format(input_file)
    if fmt == "unknown":
        typer.echo("Unsupported format")
        raise typer.Exit(code=3)

    parser = get_parser(fmt, config)
    try:
        extracted = parser.extract(input_file)
        doc = parser.to_document(extracted, input_file)
    except Exception as e:
        typer.echo(f"Inspection error: {e}")
        raise typer.Exit(code=1)

    if format == "json":
        import json

        typer.echo(json.dumps(doc.model_dump(), indent=2, ensure_ascii=False))
    else:
        typer.echo(f"Format: {fmt}")
        typer.echo(f"Blocks: {len(doc.blocks)}")
        typer.echo(f"Title: {doc.title}")


@app.command(name="config")
def config_command(
    command: str = typer.Argument(..., help="Config command (list, set, reset)"),
    key: str = typer.Option(None, "--key", help="Config key to set"),
    value: str = typer.Option(None, "--value", help="Config value to set"),
):
    """Manage configuration settings.

    COMMANDS
        list     Show all current settings.
        set      Set a key: --key <key> --value <val>.
        reset    Restore default settings (overwrites the config file).

    CONFIG KEYS
        ai_provider, base_url, model, api_key, temperature, max_tokens,
        ai_enabled, ocr_enabled, ocr_provider, ocr_language, ocr_dpi,
        output_format, extract_images, preserve_pages, cache_enabled, provider

    AI PROVIDERS (set via --key ai_provider --value <name>)
        openai-compatible  Any OpenAI-compatible API (vLLM, LM Studio, OpenRouter,
                           your xkiro endpoint). Default.
        openai             Hosted OpenAI API.
        gemini             Google Gemini API.
        ollama             Ollama running locally (native HTTP, no SDK needed).
        lm-studio          LM Studio local server (OpenAI-compatible; defaults to
                           http://localhost:1234/v1).

    EXAMPLES
        # OpenAI-compatible (e.g. xkiro)
        parsedoc config set --key ai_provider --value openai-compatible
        parsedoc config set --key base_url --value "https://api.xkiro.com/v1"
        parsedoc config set --key model --value "stealth/ox-alpha-free"
        parsedoc config set --key api_key --value "sk-xt-..."

        # Hosted OpenAI
        parsedoc config set --key ai_provider --value openai
        parsedoc config set --key base_url --value "https://api.openai.com/v1"
        parsedoc config set --key model --value "gpt-4o-mini"
        parsedoc config set --key api_key --value "sk-..."

        # Google Gemini
        parsedoc config set --key ai_provider --value gemini
        parsedoc config set --key model --value "gemini-1.5-flash"
        parsedoc config set --key api_key --value "AIza..."

        # Local Ollama
        parsedoc config set --key ai_provider --value ollama
        parsedoc config set --key base_url --value "http://localhost:11434"
        parsedoc config set --key model --value "qwen3"

        # LM Studio (OpenAI-compatible, defaults to http://localhost:1234/v1)
        parsedoc config set --key ai_provider --value lm-studio
        parsedoc config set --key model --value "local-model"

        # Behavior toggles
        parsedoc config set --key extract_images --value true
        parsedoc config set --key output_format --value markdown

    The config file is saved at ~/.config/parsedoc/config.toml and can also be
    overridden with env vars: PARSEDOC_AI_PROVIDER, PARSEDOC_BASE_URL,
    PARSEDOC_MODEL, PARSEDOC_API_KEY, PARSEDOC_OCR_LANGUAGE.
    """
    show_header()
    config = Config().load_from_file()

    if command == "list":
        console.print("[yellow]ParseDoc Configuration:[/yellow]")
        console.print(f"  Provider (parser): {config.provider}")
        console.print(f"  AI Enabled: {config.ai_enabled}")
        console.print(f"  AI Provider: {config.ai_provider}")
        console.print(f"  AI Model: {config.model}")
        console.print(f"  OCR Enabled: {config.ocr_enabled}")
        console.print(f"  Output Format: {config.output_format}")
        console.print(f"  Extract Images: {config.extract_images}")
    elif command == "set":
        if key and value is not None:
            if hasattr(config, key):
                setattr(config, key, value)
                config.save_to_file()
                console.print(f"Set {key} = {value}")
            else:
                console.print(f"Unknown config key: {key}")
        else:
            console.print("Provide --key and --value to set a config option")
    elif command == "reset":
        config.save_to_file()
        console.print("Configuration reset to defaults")
    else:
        console.print(f"Unknown config command: {command}")


@app.command(name="image")
def image_command(
    input_file: str = typer.Argument(..., help="Input DOCX file"),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for extracted images (created in the current directory by default)",
    ),
):
    """Extract embedded images from a DOCX file into a directory.

    By default images are written to '<filename>_assets' in the current
    working directory. Use -o/--output to choose another folder.
    """
    show_header()
    if not os.path.exists(input_file):
        typer.echo(f"Error: Input file '{input_file}' not found")
        raise typer.Exit(code=1)

    from .extraction.images import extract_docx_images

    stem = Path(input_file).stem
    out_dir = output or os.path.join(os.getcwd(), f"{stem}_assets")
    try:
        refs = extract_docx_images(input_file, out_dir)
    except Exception as e:
        typer.echo(f"Error extracting images: {e}")
        raise typer.Exit(code=1)

    if not refs:
        typer.echo("No images found in the document.")
        return
    typer.echo(f"✓ Extracted {len(refs)} image(s) to: {out_dir}")
    for r in refs:
        typer.echo(f"  - {r['src']}")


@app.command()
def version():
    """Show version information."""
    show_header()
    try:
        from importlib.metadata import version as _pkg_version

        pkg_ver = _pkg_version("docpilot-ai")
    except Exception:
        pkg_ver = "0.2.2"
    typer.echo(f"ParseDoc CLI Version {pkg_ver}")


if __name__ == "__main__":
    app()
