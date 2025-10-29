def get_template(config):
    origins = config.get("origins", [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:4200",
    ])
    allow_credentials = config.get("allow_credentials", True)
    allow_methods = config.get("allow_methods", ["*"])
    allow_headers = config.get("allow_headers", ["*"])

    # Serialize Python lists to literal form inside the generated file
    def to_list_literal(lst):
        return "[" + ", ".join([repr(x) for x in lst]) + "]"

    return f'''# CORS configuration for the API
# Adjust as needed for your front-end origins and allowed methods/headers

CORS_ORIGINS = {to_list_literal(origins)}
CORS_ALLOW_CREDENTIALS = {allow_credentials}
CORS_ALLOW_METHODS = {to_list_literal(allow_methods)}
CORS_ALLOW_HEADERS = {to_list_literal(allow_headers)}
'''
