"""Template pour le service Brevo"""

def get_template(config):
    return f'''
BREVO_API_KEY = "{config.get('brevo_api_key', 'YOUR_BREVO_API_KEY')}"
BREVO_SENDER_EMAIL = "{config.get('brevo_sender_email', 'no-reply@example.com')}"
BREVO_SENDER_NAME = "{config.get('brevo_sender_name', 'FastAPI App')}"

import requests

class BrevoService:
    def send_email(self, to_email: str, subject: str, body: str):
        url = "https://api.brevo.com/v3/smtp/email"
        payload = {{
            "sender": {{
                "email": BREVO_SENDER_EMAIL,
                "name": BREVO_SENDER_NAME
            }},
            "to": [{{"email": to_email}}],
            "subject": subject,
            "textContent": body
        }}
        headers = {{
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }}
        response = requests.post(url, json=payload, headers=headers)
        print("Statut:", response.status_code)
        print("Réponse:", response.json())
        return response.status_code == 200

service = BrevoService()
'''   