# ParseDoc Setup

This guide covers installing ParseDoc and configuring your AI provider (API).

> The PyPI package is named **`docpilot-ai`** (the import name and CLI command remain `parsedoc`).

---

## 1. Installation

```bash
pip install docpilot-ai
```

Upgrade an existing install:

```bash
pip install --upgrade --no-cache-dir docpilot-ai
```

### Optional dependencies

| Capability | Requirement |
|------------|-------------|
| PDF parsing | `PyMuPDF` (installed automatically) |
| DOCX / PPTX | `python-docx`, `python-pptx` (automatic) |
| HTML | `beautifulsoup4` (automatic) |
| OCR | [Tesseract](https://github.com/tesseract-ocr/tesseract) + `pytesseract` (automatic) |

---

## 2. Verify the install

```bash
parsedoc version
```

You should see the ParseDoc banner and the installed version.

---

## 3. Configure your AI API

ParseDoc supports several providers. Choose **one** of the three methods below.

### Method A — `parsedoc config` commands (recommended)

```bash
parsedoc config set --key ai_provider --value openai-compatible
parsedoc config set --key base_url --value "https://api.xkiro.com/v1"
parsedoc config set --key model --value "stealth/ox-alpha-free"
parsedoc config set --key api_key --value "sk-xt-eaf8b7bb622b5226a41820e5f3360f7643db5e7cdc562494"
```

Verify what is saved:

```bash
parsedoc config list
```

### Method B — Environment variables (good for scripts / CI)

```bash
export PARSEDOC_AI_PROVIDER=openai-compatible
export PARSEDOC_BASE_URL="https://api.xkiro.com/v1"
export PARSEDOC_MODEL="stealth/ox-alpha-free"
export PARSEDOC_API_KEY="sk-xt-eaf8b7bb622b5226a41820e5f3360f7643db5e7cdc562494"
```

Environment variables override the saved config file.

### Method C — Edit the config file directly

Location: `~/.config/parsedoc/config.toml`

```toml
[ai]
enabled = true
provider = "openai-compatible"
base_url = "https://api.xkiro.com/v1"
model = "stealth/ox-alpha-free"
api_key = "sk-xt-eaf8b7bb622b5226a41820e5f3360f7643db5e7cdc562494"
temperature = 0.2
max_tokens = 4096
```

To restore defaults at any time:

```bash
parsedoc config reset
```

---

## 4. Supported AI providers

Set the provider with `parsedoc config set --key ai_provider --value <name>`:

| Provider | Meaning | Example model |
|----------|---------|---------------|
| `openai-compatible` | Any OpenAI-compatible API (vLLM, LM Studio, OpenRouter, xkiro) — **default** | `stealth/ox-alpha-free` |
| `openai` | Hosted OpenAI API | `gpt-4o-mini` |
| `gemini` | Google Gemini API | `gemini-1.5-flash` |
| `ollama` | Ollama running locally (native HTTP) | `qwen3` |
| `lm-studio` | LM Studio local server (defaults to `http://localhost:1234/v1`) | `local-model` |

Example — LM Studio (no `base_url` needed):

```bash
parsedoc config set --key ai_provider --value lm-studio
parsedoc config set --key model --value local-model
```

Example — hosted OpenAI:

```bash
parsedoc config set --key ai_provider --value openai
parsedoc config set --key base_url --value "https://api.openai.com/v1"
parsedoc config set --key model --value "gpt-4o-mini"
parsedoc config set --key api_key --value "sk-..."
```

---

## 5. Run a conversion

Once configured, the saved settings are used automatically:

```bash
# Single file
parsedoc convert input.docx -o output.md --mode hybrid

# Whole folder (creates ./batch_out in the current directory)
parsedoc batch . -p "*.docx"
```

Modes: `local` (no AI, fast & private), `ai` (AI-only), `hybrid` (AI with automatic local fallback).

> If the AI provider is flaky or returns nothing, `hybrid` mode falls back to the
> local rule-based structurer, which still preserves document formatting
> (headings, bold/italic, lists, tables).
