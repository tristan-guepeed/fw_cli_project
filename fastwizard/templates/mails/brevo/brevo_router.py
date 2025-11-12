"""Template pour le router Brevo"""

def get_template(config):
    return f'''
from fastapi import APIRouter, HTTPException
from .brevo_service import service  # doit correspondre au service généré

router = APIRouter()

@router.post("/send")
async def send_email(to_email: str, subject: str, body: str):
    success = service.send_email(to_email, subject, body)
    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi")
    return {{"status": "sent", "service": "brevo"}}
'''
