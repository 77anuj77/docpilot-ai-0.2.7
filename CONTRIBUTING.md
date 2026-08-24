# Contributing to ParseDoc

Thanks for your interest in improving ParseDoc! This guide covers local
development, the project layout, how to extend parsers and AI providers, and
where the project is heading (including **MCP SDK** integration).

> The PyPI package is named **`docpilot-ai`**; the import name and CLI command
> are both `parsedoc`.

## Development setup

```bash
git clone <repo-url>
cd parsedoc
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]      # editable install + dev tools (pytest, ruff, mypy)
pip install build twine    # for building & publishing
```

Run the CLI from the source tree during development:

```bash
PYTHONPATH=src python -m parsedoc version
PYTHONPATH=src python -m parsedoc convert file.docx -o out.md --mode local
```

## Project layout

```
parsedoc/
├── cli.py                 # Typer CLI (commands: convert, batch, inspect, config, version)
├── core/                  # config, detection, pipeline, chunking
├── parsers/               # format parsers (pdf, docx, pptx, html, image, text)
├── extraction/            # text/table/image/layout extraction helpers
├── ai/                    # AIProvider abstraction + provider implementations
├── schema/                # Document/Block pydantic models
├── renderers/             # markdown / html / json / text renderers
├── ocr/                   # OCR providers (tesseract)
└── utils/                 # filesystem, logging helpers
```

The pipeline is intentionally layered:

**libraries extract facts → optional AI understands structure → deterministic renderer emits Markdown.**

## Adding a new document parser

1. Create `src/parsedoc/parsers/<fmt>.py` subclassing `BaseParser`.
2. Implement `detect_format`, `extract` (return `{"text", "tables", "blocks", "title"}`),
   and `to_document`.
3. Register it in `parsers/__init__.py::PARSER_REGISTRY`.
4. Add the format to `core/detection.py::EXTENSION_MAP`.

Keep extraction format-agnostic: return structured `blocks` so both the local
renderer and the AI path benefit.

## Adding a new AI provider

1. Create `src/parsedoc/ai/<name>.py` subclassing `AIProvider` and implementing
   `generate(prompt, content) -> str`.
2. Wire it into `ai/base.py::build_provider` (factory).
3. Document it in `setup.md` and the README provider table.

Providers should accept `base_url`, `model`, and `api_key` so they can be
configured via `parsedoc config set` or environment variables.

## Running tests & linting

```bash
pytest
ruff check src
mypy src
```

## Future integrations: MCP SDK

ParseDoc is a natural fit for **agentic** workflows. Planned work is to expose
ParseDoc as an [MCP](https://modelcontextprotocol.io) server so LLM agents can
call it as a tool:

- Add `mcp` (the Model Context Protocol Python SDK) as an optional dependency.
- Implement an `mcp` server entry point that registers tools such as
  `convert_document` (input file + options → Markdown) and `inspect_document`.
- Reuse the existing `core.pipeline.Pipeline` so the MCP tools share the exact
  same conversion logic as the CLI.
- Keep the MCP server optional (`pip install docpilot-ai[mcp]`) so the core
  package stays lightweight.

Contributions that move this forward (or add new parsers/providers) are very
welcome.

## Release process

1. Bump `version` in `pyproject.toml`.
2. `python -m build`
3. `twine upload dist/*`
4. Tag the release: `git tag vX.Y.Z && git push --tags`.

## Pull requests

- Keep changes focused; add tests for new parsers/providers.
- Run `ruff` and `pytest` before opening a PR.
- Update `README.md` / `setup.md` / `CONTRIBUTING.md` when behavior changes.
