""" pynchon.constants
"""

import os
from pathlib import Path

GLYPH_COMPLEXITY = "🐉 Complex"

PYNCHON_ROOT = os.environ.get("PYNCHON_ROOT", None)
PYNCHON_CONFIG = os.environ.get("PYNCHON_CONFIG", None)
LOG_LEVEL = os.environ.get("PYNCHON_LOG_LEVEL", "WARNING")

CONF_FILE_SEARCH_ORDER = ["pynchon.json5", ".pynchon.json5", "pyproject.toml"]
DEFAULT_PLUGINS = [
    "core",
    "git",
    # "pandoc",  # required by markdown
    "markdown",
    "src",
    "docs",
    "parse",
    "pattern",
    "plugins",
    "project",
    "globals",
    "github",  # NB: used by `pynchon pattern sync . github`
    "python",
    "gen",
    "render",
    "json",
    "jinja",
]
PYNCHON_EMBEDDED_TEMPLATES_ROOT = PETR = Path(__file__).parents[0] / "templates"
PYNCHON_CORE_INCLUDES_DIRS = (PYNCHON_EMBEDDED_TEMPLATES_ROOT / "includes",)
for _p in PYNCHON_CORE_INCLUDES_DIRS:
    assert _p.exists()

# TEMPLATE_DIR = os.environ.get(
#     "PYNCHON_TEMPLATE_DIR",
#     os.path.join(
#         os.path.dirname(__file__),
#         "templates",
#     ),
# )
#


# # FIXME: reuse parallel jinja env/template stuff in pynchon.util.text.render
# plugin_base = "pynchon/plugins"
# T_DETAIL_CLI = ENV.get_template(f"{plugin_base}/python/cli/detail.md.j2")
# T_TOC_CLI = ENV.get_template(f"{plugin_base}/python/cli/TOC.md.j2")
# T_VERSION_METADATA = ENV.get_template(f"{plugin_base}/core/VERSIONS.md.j2")
# T_CLI_MAIN_MODULE = ENV.get_template(f"{plugin_base}/python/cli/main.module.md.j2")
