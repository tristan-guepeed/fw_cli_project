"""
Template pour l'initialisation de Ruff & Black
"""
def get_template(config):
    return r"""[tool.black]
line-length = 88
target-version = ["py311"]
exclude = '''
/(
    \.venv
  | venv
  | __pycache__
  | alembic
)/
'''

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "W", "C90", "I"]
ignore = ["E501"]
exclude = [
    "__init__.py",
    ".venv",
    "venv",
    "__pycache__",
    "*alembic*"
]
"""
