import os
import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from database import SessionLocal
from models.outros_encontros import OutroEncontro  # sua tabela
from routers.contactos import tipo_tabela

# ==========================
# 📩 Envio de SMS usando endpoint
# ==========================
async def enviar_sms_api(mensagem, numeros):
    """
    Envia SMS via endpoint /sms/enviar.
    Aceita um número ou lista de números.
    """
    if not isinstance(numeros, list):
        numeros = [numeros]

    base_url = os.getenv("RENDER_EXTERNAL_URL") or "http://127.0.0.1:8000"
    url = f"{base_url}/sms/enviar"

    payload = {
        "sender_id": "ESG-DUNDA",
        "mensagem": mensagem,
        "numeros": numeros
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(url, json=payload)
            return resp.status_code == 200
        except Exception as e:
            print(f"⚠️ Exception ao enviar SMS: {e}")
            return False

# ==========================
# 📞 Pegar números da tabela de contactos
# ==========================
async def pegar_numeros(tipo):
    if tipo not in tipo_tabela:
        return []
    Model = tipo_tabela[tipo]
    async with SessionLocal() as db:
        result = await db.execute(select(Model))
        contactos = result.scalars().all()
        numeros = [c.telefone for c in contactos if c.telefone]
        return numeros

# ==========================
# 🔄 Monitor automático para outros_encontros
# ==========================
async def monitorar_outros_encontros():
    print("🔄 Monitor automático de outros_encontros iniciado")

    while True:
        agora = datetime.now()
        proxima_hora = (agora.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        tempo_ate_proxima_hora = (proxima_hora - agora).total_seconds()

        # Espera até o início da próxima hora
        await asyncio.sleep(tempo_ate_proxima_hora)

        async with SessionLocal() as db:
            result = await db.execute(
                select(OutroEncontro).where(OutroEncontro.status == "APROVADO")
            )
            encontros = result.scalars().all()

            for encontro in encontros:

                # ==========================
                # 🔔 ALERTA (2 dias antes)
                # ==========================
                momento_alerta = encontro.data_hora - timedelta(days=2)
                if encontro.alerta_enviado == "NAO" and agora >= momento_alerta:
                    numeros_alerta = await pegar_numeros("diretor")
                    if numeros_alerta:
                        mensagem_alerta = (
                            f"Saudacoes, ha um encontro referente a {encontro.titulo}, "
                            f"agendado para {encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h. "
                            f"Se pretende adiar ou cancelar, entre no sistema."
                        )
                        sucesso = await enviar_sms_api(mensagem_alerta, numeros_alerta)
                        if sucesso:
                            await db.execute(
                                update(OutroEncontro)
                                .where(OutroEncontro.id == encontro.id)
                                .values(alerta_enviado="SIM")
                            )
                            await db.commit()

                # ==========================
                # 📢 CONVOCATÓRIA (1 dia antes)
                # ==========================
                momento_convocatoria = encontro.data_hora - timedelta(days=1)
                if encontro.convocatoria_enviada == "NAO" and agora >= momento_convocatoria:
                    enviados = 0
                    total = len(encontro.contactos)
                    for nome, numero in zip(encontro.nomes, encontro.contactos):
                        mensagem_convocatoria = (
                            f"Saudacoes sr(a) {nome}, esta convocado(a) para um encontro de {encontro.titulo}, a ter lugar no dia {encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h, no(a) {encontro.local}. Pede-se pontualidade."
                        )
                        sucesso = await enviar_sms_api(mensagem_convocatoria, numero)
                        if sucesso:
                            enviados += 1
                        await asyncio.sleep(5)  # intervalo entre envios

                    if total > 0 and enviados == total:
                        await db.execute(
                            update(OutroEncontro)
                            .where(OutroEncontro.id == encontro.id)
                            .values(convocatoria_enviada="SIM")
                        )
                        await db.commit()

# ==========================
# Inicializa monitor
# ==========================
async def main():
    await monitorar_outros_encontros()

if __name__ == "__main__":
    asyncio.run(main())