from pathlib import Path

def get_initial_migration(project_path: Path, include_user: bool = False) -> None:
    """
    Crée une migration initiale Alembic si inexistante.
    
    Args:
        project_path: chemin du projet
        include_user: si True, crée la table users (module auth-jwt présent)
    """
    versions_dir = project_path / "alembic" / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)

    existing = list(versions_dir.glob("*_init.py"))
    if existing:
        return

    revision_id = "0001"
    filename = versions_dir / f"{revision_id}_init.py"

    if include_user:
        migration_content = f'''"""initial schema"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "{revision_id}"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False, unique=True, index=True),
        sa.Column("email", sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("users")
'''
    else:
        migration_content = f'''"""initial schema (empty)"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "{revision_id}"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
'''

    filename.write_text(migration_content)
