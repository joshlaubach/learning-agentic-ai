"""A real local MCP server, spawned as a subprocess over stdio by
curriculum/07_tool_integration.ipynb. Not a mock: the notebook's MCP client connects to it
and calls it directly. See PROGRESS.md's Unit 8 notes for why this uses PyPI's live JSON API
(real, reachable, needs no vendored cache mechanism) rather than the spec's originally
suggested GH Archive dataset (Hugging-Face-hosted, unreachable from this build environment --
the same class of block noted for SQuAD in Unit 4 and tiktoken in Unit 6).
"""

import json
import sys
from pathlib import Path

import requests
from mcp.server.fastmcp import FastMCP

_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "pypi_cache"
_FIELDS = ["name", "version", "summary", "license", "home_page", "project_urls"]

mcp = FastMCP("pypi-lookup")


@mcp.tool()
def get_package_info(package_name: str) -> dict:
    """Look up real package metadata (name, version, summary, license, project URLs) for a
    package on PyPI. Reads from a local cache if present; falls back to a live PyPI query
    otherwise -- either way, the data returned is real, not fabricated."""
    cache_path = _CACHE_DIR / f"{package_name}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
    response.raise_for_status()
    info = response.json()["info"]
    return {field: info.get(field) for field in _FIELDS}


if __name__ == "__main__":
    mcp.run(transport="stdio")
