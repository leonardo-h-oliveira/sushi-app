"""Read-only probes for a deployed API; no customer or staff credentials required."""
import argparse
import json
from urllib.request import urlopen
from urllib.parse import urlsplit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("api_url")
    parser.add_argument("--require-closed", action="store_true")
    args = parser.parse_args()
    parsed = urlsplit(args.api_url)
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.query:
        raise SystemExit("Use the public HTTPS API base URL without credentials or query parameters.")
    try:
        results = {}
        for path in ["/health", "/ready", "/store-settings", "/products"]:
            with urlopen(args.api_url.rstrip("/") + path, timeout=20) as response:
                results[path] = json.load(response)
        assert results["/health"]["status"] == "ok"
        assert results["/ready"]["status"] == "ready"
        assert isinstance(results["/products"], list) and results["/products"]
        if args.require_closed:
            assert results["/store-settings"]["is_open"] is False
        print(json.dumps({"api": "reachable", "database": "ready", "catalog": "available", "ordering_open": results["/store-settings"]["is_open"]}))
    except Exception:
        raise SystemExit("Deployment checks failed. Inspect the readiness endpoint and private deployment logs.")
