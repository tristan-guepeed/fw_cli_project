"""Template pour le modèle utilisateur"""
def get_template(config):

    selected_modules = config.get("selected_modules", [])
    oauth_module = next((m for m in selected_modules if m.startswith("auth-oauth")), None)

    if oauth_module == "auth-oauth-google":
        oauth_functions = '''
    oauth_provider = Column(String, nullable=True)
    oauth_account_created_at = Column(DateTime, nullable=True)
    google_id = Column(String, nullable=True, unique=True)
'''
    elif oauth_module == "auth-oauth-github":
        oauth_functions = '''
    oauth_provider = Column(String, nullable=True)
    oauth_account_created_at = Column(DateTime, nullable=True)
    github_id = Column(String, nullable=True, unique=True)
'''
    else:
        oauth_functions = ''
    return '''from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """Modèle utilisateur pour l'authentification"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
''' + oauth_functions + ''' 
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
'''