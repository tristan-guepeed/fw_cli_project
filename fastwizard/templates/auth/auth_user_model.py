"""Template pour le modèle utilisateur"""
def get_template(config):

    selected_modules = config.get("selected_modules", [])
    custom_roles = config.get("custom_roles", [])
    oauth_module = next((m for m in selected_modules if m.startswith("auth-oauth")), None)

    oauth_functions = """
    oauth_provider = Column(String, nullable=True)
    oauth_account_created_at = Column(DateTime, nullable=True)
    """
    
    if "auth-oauth-google" in selected_modules and "auth-oauth-github" in selected_modules:
        oauth_functions += """
    google_id = Column(String, nullable=True, unique=True)
    github_id = Column(String, nullable=True, unique=True)
    """
    elif "auth-oauth-google" in selected_modules:
        oauth_functions += """
    google_id = Column(String, nullable=True, unique=True)
    """
    elif "auth-oauth-github" in selected_modules:
        oauth_functions += """
    github_id = Column(String, nullable=True, unique=True)
    """
    
    all_roles = ["admin", "user"] + custom_roles
    roles_list_str = ", ".join(f'"{r}"' for r in all_roles)

    return f'''from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    DEFAULT_ROLES = [{roles_list_str}]

class User(Base):
    """Modèle utilisateur pour l'authentification"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
''' + oauth_functions + ''' 
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
'''