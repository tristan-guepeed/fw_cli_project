"""Template pour le service Mailjet"""

def get_template(config):
    mailjet_api_key = config.get('mailjet_api_key', 'YOUR_MAILJET_API_KEY')
    mailjet_api_secret = config.get('mailjet_api_secret', 'YOUR_MAILJET_API_SECRET')
    mailjet_sender_email = config.get('mailjet_sender_email', 'no-reply@example.com')
    mailjet_sender_name = config.get('mailjet_sender_name', 'FastAPI App')

    return f'''
MAILJET_API_KEY = "{mailjet_api_key}"
MAILJET_API_SECRET = "{mailjet_api_secret}"
MAILJET_SENDER_EMAIL = "{mailjet_sender_email}"
MAILJET_SENDER_NAME = "{mailjet_sender_name}"

import requests

class MailjetService:
    def send_email(self, to_email: str, subject: str, body: str):
        url = "https://api.mailjet.com/v3.1/send"
        data = {{
            "Messages": [
                {{
                    "From": {{
                        "Email": MAILJET_SENDER_EMAIL,
                        "Name": MAILJET_SENDER_NAME
                    }},
                    "To": [{{"Email": to_email}}],
                    "Subject": subject,
                    "TextPart": body
                }}
            ]
        }}
        auth = (MAILJET_API_KEY, MAILJET_API_SECRET)
        response = requests.post(url, json=data, auth=auth)
        print("Statut:", response.status_code)
        print("Réponse:", response.json())
        return response.status_code == 200

service = MailjetService()
'''   