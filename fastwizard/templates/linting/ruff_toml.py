"""
Template pour l'initialisation de Ruff
"""
def get_template(config):
    return '''[tool.black]
line-length = 88
target-version = ["py311"]

[tool.ruff]
line-length = 88
select = ["E", "F", "W", "C90", "I"]
ignore = ["E501", "W503"]
exclude = ["__init__.py", "venv", "__pycache__", "*alembic*"]
'''