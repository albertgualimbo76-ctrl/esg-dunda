from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

router = APIRouter(prefix="/mozesms", tags=["MozeSMS"])

# 🔴 Credenciais (como você pediu)
API_KEY = 'mk_7cef2d3000ed1336907ba646a657374e'
API_SECRET = 'sk_26390bd190cfe2ab6871d577293bd07b616db33ea0d50c843a0afdfde937fe30'

API_URL = 'https://apiv4.mozesms.com/billing/purchase'


# ==========================
# Schema
# ==========================
class CompraRequest(BaseModel):
    amount: float
    gateway: str
    phone: str | None = None


# ==========================
# Serviço interno
# ==========================
def fazer_compra(valor, gateway, phone=None):
    dados = {
        "amount": valor,
        "gateway": gateway
    }

    if gateway in ['mpesa', 'emola']:
        if not phone:
            raise ValueError("Número de telefone obrigatório para M-Pesa e E-Mola")
        dados["customer_phone"] = phone

    headers = {
        'X-API-Key': API_KEY,
        'X-API-Secret': API_SECRET,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(API_URL, headers=headers, json=dados, timeout=10)
        return response

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão: {str(e)}")


# ==========================
# Endpoint
# ==========================
@router.post("/comprar-creditos")
def comprar_creditos(req: CompraRequest):
    try:
        response = fazer_compra(req.amount, req.gateway, req.phone)

        if response.status_code == 201:
            return {
                "status": "sucesso",
                "transacao": response.json()
            }

        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))