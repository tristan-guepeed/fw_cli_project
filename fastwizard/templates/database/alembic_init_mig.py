"""Template pour la première migration Alembic"""
def get_template(config):
    """
    Génère le contenu de la migration initiale Alembic avec :
    - table roles
    - table users
    - insertion des rôles par défaut + personnalisés
    - création de l'utilisateur admin
    
    Args:
        config: Dictionnaire de configuration avec les clés optionnelles:
            - revision (str): Identifiant de la révision (défaut: "0001_initial")
            - description (str): Description de la migration
            - custom_roles (List[str]): Liste des rôles personnalisés à ajouter
            - admin_username (str): Nom d'utilisateur de l'admin (défaut: "user")
            - admin_email (str): Email de l'admin (défaut: "admin@user.com")
            - admin_password (str): Mot de passe de l'admin (défaut: "admin")
            - admin_role (str): Rôle de l'admin (défaut: "admin")
            - use_bcrypt_direct (bool): Si True, utilise bcrypt directement (défaut: False)
            - timezone_aware (bool): Si True, utilise DateTime avec timezone (défaut: True)
    
    Returns:
        str: Contenu du fichier de migration Python
    """
    # Rôles par défaut
    default_roles = ["admin", "user"]
    # Ajouter les rôles personnalisés si fournis dans le config
    custom_roles = config.get("custom_roles", [])
    all_roles = default_roles + custom_roles

    selected_modules = config.get("selected_modules", [])
    oauth_functions = """
        sa.Column("oauth_provider", sa.String(length=50), nullable=True),
        sa.Column("oauth_account_created_at", sa.DateTime(), nullable=True),
    """
    
    if "auth-oauth-google" in selected_modules and "auth-oauth-github" in selected_modules:
        oauth_functions += """
        sa.Column("google_id", sa.String(length=50), nullable=True, unique=True),
        sa.Column("github_id", sa.String(length=50), nullable=True, unique=True),
    """
    elif "auth-oauth-google" in selected_modules:
        oauth_functions += """
        sa.Column("google_id", sa.String(length=50), nullable=True, unique=True),
    """
    elif "auth-oauth-github" in selected_modules:
        oauth_functions += """
        sa.Column("github_id", sa.String(length=50), nullable=True, unique=True),
    """

    # Paramètres
    revision = config.get("revision", "0001_initial")
    description = config.get("description", "Initial migration Alembic: tables Role & User, default roles, admin user")
    admin_username = config.get("admin_username", "user")
    admin_email = config.get("admin_email", "admin@user.com")
    admin_password = config.get("admin_password", "admin")
    admin_role = config.get("admin_role", "admin")
    use_bcrypt_direct = config.get("use_bcrypt_direct", False)
    timezone_aware = config.get("timezone_aware", True)
    
    # Validation
    if admin_role not in all_roles:
        raise ValueError(f"admin_role '{admin_role}' doit être dans les rôles (default + custom): {all_roles}")
    
    # Import de la librairie de hachage
    if use_bcrypt_direct:
        hash_import = "import bcrypt"
        hash_setup = ""
        hash_code = f'''    # Hachage avec bcrypt directement
    password = "{admin_password}".encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')'''
    else:
        hash_import = "from passlib.context import CryptContext"
        hash_setup = '''
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
'''
        hash_code = f'''    # Hachage du mot de passe
    hashed_password = pwd_context.hash("{admin_password}")'''
    
    # Configuration timezone
    datetime_type = "sa.DateTime(timezone=True)" if timezone_aware else "sa.DateTime()"
    
    # Génération de la liste des rôles pour l'insertion (default + custom)
    roles_list = ",\n            ".join([f'{{"name": "{role}"}}' for role in all_roles])
    
    template = f'''"""Initial migration Alembic: tables Role & User, default roles, admin user"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
{hash_import}
from datetime import datetime

# Alembic identifiers
revision = "{revision}"
down_revision = None
branch_labels = None
depends_on = None
{hash_setup}

def upgrade() -> None:
    # --- Création de la table roles ---
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
    )

    # --- Création de la table users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("username", sa.String(length=50), nullable=False, unique=True, index=True),
        sa.Column("email", sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("created_at", {datetime_type}, server_default=func.now()),
        sa.Column("updated_at", {datetime_type}, nullable=True, onupdate=func.now()),
        {oauth_functions}
    )

    # --- Insertion des rôles par défaut ---
    roles_table = table(
        "roles",
        column("id", Integer),
        column("name", String)
    )
    
    op.bulk_insert(
        roles_table,
        [
            {roles_list}
        ]
    )

    # --- Création de l'utilisateur admin ---
    connection = op.get_bind()
    role_id_admin = connection.execute(
        sa.text("SELECT id FROM roles WHERE name='{admin_role}'")
    ).scalar()
    
{hash_code}

    users_table = table(
        "users",
        column("id", Integer),
        column("username", String),
        column("email", String),
        column("hashed_password", String),
        column("is_active", Boolean),
        column("role_id", Integer),
        column("created_at", DateTime)
    )

    op.bulk_insert(
        users_table,
        [
            {{
                "username": "{admin_username}",
                "email": "{admin_email}",
                "hashed_password": hashed_password,
                "is_active": True,
                "role_id": role_id_admin,
                "created_at": datetime.utcnow()
            }}
        ]
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("roles")
'''
    
    return template