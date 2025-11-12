from pathlib import Path
from typing import List

from fastwizard.templates.main.main_template import get_main_template
from fastwizard.generator.submodules.requirements import generate_requirements
from fastwizard.templates.main.env import generate_env_example
from fastwizard.templates.main.readme import generate_readme
from fastwizard.templates.main.gitignore import get_gitignore_template
from fastwizard.templates.main.makefile import generate_makefile

def generate_main_files(
    project_path: Path,
    project_name: str,
    selected_modules: List[str],
    db_config: dict,
    module_manager,
):
    """Génère les fichiers principaux du projet"""

    # main.py
    main_content = get_main_template(project_name, selected_modules)
    (project_path / "main.py").write_text(main_content)

    # requirements.txt
    requirements = generate_requirements(module_manager, selected_modules)
    (project_path / "requirements.txt").write_text(requirements)

    # .env.example
    env_content = generate_env_example(selected_modules, db_config)
    (project_path / ".env.example").write_text(env_content)

    # README.md
    readme_content = generate_readme(project_name, selected_modules)
    (project_path / "README.md").write_text(readme_content)

    # .gitignore
    gitignore_content = get_gitignore_template()
    (project_path / ".gitignore").write_text(gitignore_content)

    # Makefile
    if "makefile" in selected_modules:
        makefile_content = generate_makefile(selected_modules)
        (project_path / "Makefile").write_text(makefile_content)