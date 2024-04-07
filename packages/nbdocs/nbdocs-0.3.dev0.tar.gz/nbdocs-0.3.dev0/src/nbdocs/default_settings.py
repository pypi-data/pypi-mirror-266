# settings schema for nbdocs and mkdocs.yaml

NBDOCS_SETTINGS = """[nbdocs]
docs_path = docs
notebooks_path = nbs
images_path = images
"""


MKDOCS_BASE = """site_name: Your site name
# repo_url: Your repo url
# repo_name: Your repo name
# docs_dir: docs  # The docs directory.

# copyright:
"""

MATERIAL_BASE = """theme:
  name: material
  custom_dir: docs/overrides

  palette:
    - scheme: default
      toggle:
        icon: material/toggle-switch-off-outline
        name: Switch to dark mode
    - scheme: slate
      toggle:
        icon: material/toggle-switch
        name: Switch to light mode
markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
"""

FOOTER_HTML = """<div class="md-copyright">
  {% if config.copyright %}
    <div class="md-copyright__highlight">
      {{ config.copyright }}
    </div>
  {% endif %}
  {% if not config.extra.generator == false %}
    Made with
    <a href="https://github.com/ayasyrev/nbdocs" target="_blank" rel="noopener">
      NbDocs
    </a>
        and
    <a href="https://squidfunk.github.io/mkdocs-material/" target="_blank" rel="noopener">
      Material for MkDocs
    </a>
  {% endif %}
</div>
"""
