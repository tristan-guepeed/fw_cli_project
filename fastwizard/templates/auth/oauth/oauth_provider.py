"""Template pour le provider OAuth"""
def get_template(config):
    provider = config.get("provider", "")
    auth_url = config.get("auth_url", "")
    token_url = config.get("token_url", "")
    user_info_url = config.get("user_info_url", "")
    client_id = config.get("client_id", "")
    client_secret = config.get("client_secret", "")
    redirect_uri = config.get("redirect_uri", "")

    return f'''
# OAuth Provider configuration
PROVIDER = "{provider}"
AUTH_URL = "{auth_url}"
TOKEN_URL = "{token_url}"
USER_INFO_URL = "{user_info_url}"
CLIENT_ID = "{client_id}"
CLIENT_SECRET = "{client_secret}"
REDIRECT_URI = "{redirect_uri}"
'''
