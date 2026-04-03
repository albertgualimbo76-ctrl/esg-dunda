from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

# 🔐 Token da conta ESG-DUNDA
MOZESMS_TOKEN = "bWtfNGEyMTVjMzA1OGQ5ZTEyNDU1YWFmZWRmNTBhM2FlNDI6NDI4Mjpza19kMTNmYWNkMzE2YmU4YjQxM2ZhNDZlZmRjZWRkM2ViZWM3ZDc1OTBkMWJkN2I3ZTRjZmExY2JmMmZhYWRkYWRk"

MOZESMS_URL = "https://api.mozesms.com/v1/sms/bulk"

# 🔥 Sender ID
SENDER_ID = "ESG-DUNDA"

# ✅ CRIAR ROUTER (em vez de FastAPI)
router = APIRouter(
    prefix="/sms",
    tags=["SMS"]
)

# ==========================
# Modelo de entrada
# ==========================
class SmsRequest(BaseModel):
    mensagem: str
    numeros: list[str]

# ==========================
# Endpoint enviar SMS
# ==========================
@router.post("/enviar")
async def enviar_sms(request: SmsRequest):

    payload = {
        "from": SENDER_ID,
        "messages": [
            {"to": numero, "text": request.mensagem}
            for numero in request.numeros
        ]
    }

    headers = {
        "Authorization": f"Bearer {MOZESMS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                MOZESMS_URL,
                headers=headers,
                json=payload
            )

        try:
            resposta_api = response.json()
        except Exception:
            resposta_api = response.text

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=resposta_api
            )

        return {
            "message": "Enviado com sucesso!",
            "response": resposta_api
        }

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro de conexão: {str(e)}"
        )