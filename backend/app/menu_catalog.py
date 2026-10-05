"""Menu catalog imported from the public Sushi Poços storefront."""

import json
from pathlib import Path
from typing import Any


_CATALOG_PATH = Path(__file__).with_name("menu_data.json")
_CATALOG: dict[str, list[dict[str, Any]]] = json.loads(
    _CATALOG_PATH.read_text(encoding="utf-8")
)

CATEGORIES = _CATALOG["categories"]
PRODUCTS = _CATALOG["products"]
