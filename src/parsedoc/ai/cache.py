"""ParseDoc AI Cache (PRD #22, #46)"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Optional

from ..utils.filesystem import default_cache_dir


def _hash_inputs(content: str, model: str, prompt_version: str, config_hash: str) -> str:
    payload = f"{content}|{model}|{prompt_version}|{config_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _config_hash(config: Dict) -> str:
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode("utf-8")).hexdigest()


def cache_path() -> Path:
    path = Path(default_cache_dir())
    path.mkdir(parents=True, exist_ok=True)
    return path / "ai_cache.json"


def get_cache() -> Dict:
    p = cache_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def lookup(content: str, model: str, prompt_version: str, config: Dict) -> Optional[str]:
    cache = get_cache()
    key = _hash_inputs(content, model, prompt_version, _config_hash(config))
    return cache.get(key)


def store(content: str, model: str, prompt_version: str, config: Dict, result: str):
    cache = get_cache()
    key = _hash_inputs(content, model, prompt_version, _config_hash(config))
    cache[key] = result
    cache_path().write_text(json.dumps(cache, indent=2), encoding="utf-8")
