"""ParseDoc JSON renderer"""

import json

from ..schema.document import Document


def render_json(doc: Document) -> str:
    """Render a Document model to a JSON string."""
    return json.dumps(doc.model_dump(), indent=2, ensure_ascii=False)
