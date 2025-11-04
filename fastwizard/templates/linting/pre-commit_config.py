# fastwizard/templates/pre_commit_config.py
def get_template(config):
    return """
repos:
  - repo: local
    hooks:
      - id: ruff
        name: "Ruff linter"
        entry: ruff
        language: system
        types: [python]
        args: ["--fix"]

      - id: black
        name: "Black formatter"
        entry: black
        language: system
        types: [python]
        args: ["--line-length", "88"]
"""
