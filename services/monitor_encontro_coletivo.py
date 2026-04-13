import os
import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update

from database import SessionLocal
from models.encontro_coletivo import EncontroColetivo
from routers.contactos import tipo_tabela


# ==========================
# 📩 Enviar SMS via API
# ==========================
async def enviar_sms_api(mensagem, numeros):
    base_url = os.getenv("RENDER_EXTERNAL_URL") or "http://127.0.0.1:8000"
    url = f"{base_url}/sms/enviar"

    if not isinstance(numeros, list):
        numeros = [numeros]

    payload = {
        "sender_id": "ESG-DUNDA",
        "mensagem": mensagem,
        "numeros": numeros
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                print("✅ SMS enviado:", numeros)
                return True
            else:
                print("❌ Erro SMS:", resp.text)
                return False
        except Exception as e:
            print("⚠️ Erro ao enviar SMS:", e)
            return False


# ==========================
# 📞 Buscar números por tipo
# ==========================
async def pegar_numeros(tipo):
    if tipo not in tipo_tabela:
        return []

    Model = tipo_tabela[tipo]

    async with SessionLocal() as db:
        result = await db.execute(select(Model))
        contactos = result.scalars().all()
        numeros = [c.telefone for c in contactos if c.telefone]

        print(f"📞 Números {tipo}: {numeros}")
        return numeros


# ==========================
# 🔄 MONITOR (EXECUÇÃO ÚNICA)
# ==========================
async def monitorar_encontros_coletivo():
    print("🔄 Monitor de encontros COLETIVO iniciado")

    agora = datetime.now()

    async with SessionLocal() as db:
        result = await db.execute(
            select(EncontroColetivo).where(EncontroColetivo.status == "APROVADO")
        )
        encontros = result.scalars().all()

        for encontro in encontros:

            # 🔥 Buscar números
            numeros_diretor = await pegar_numeros("diretor")
            numeros_direcao = await pegar_numeros("direcao")
            numeros = list(set(numeros_diretor + numeros_direcao))

            # ==========================
            # 🔔 ALERTA (2 dias antes)
            # ==========================
            momento_alerta = encontro.data_hora - timedelta(days=2)

            if encontro.alerta_enviado == "NAO" and agora < encontro.data_hora:

                if agora >= momento_alerta:
                    mensagem_alerta = (
                        f"Saudacoes, ha um encontro do colectivo referente a "
                        f"{encontro.titulo} agendado para "
                        f"{encontro.data_hora.strftime('%d/%m/%Y, %H:%M')}h."
                    )

                    sucesso = await enviar_sms_api(mensagem_alerta, numeros)

                    if sucesso:
                        await db.execute(
                            update(EncontroColetivo)
                            .where(EncontroColetivo.id == encontro.id)
                            .values(alerta_enviado="SIM")
                        )
                        await db.commit()

                        print(f"✅ Alerta COLETIVO enviado (ID {encontro.id})")

            # ==========================
            # 📢 CONVOCATÓRIA (1 dia antes)
            # ==========================
            momento_conv = encontro.data_hora - timedelta(days=1)

            if encontro.convocatoria_enviada == "NAO" and agora < encontro.data_hora:

                if agora >= momento_conv:
                    mensagem_conv = (
                        f"Incumbe me o Exmo Senhor Director da escola em convocar todos membros de direcção para participarem na {encontro.titulo}, "
                        f"no dia {encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h no gabinete da Directora."
                    )

                    enviados = 0
                    total = len(numeros)

                    for numero in numeros:
                        ok = await enviar_sms_api(mensagem_conv, numero)
                        if ok:
                            enviados += 1
                        await asyncio.sleep(5)

                    if total > 0 and enviados == total:
                        await db.execute(
                            update(EncontroColetivo)
                            .where(EncontroColetivo.id == encontro.id)
                            .values(convocatoria_enviada="SIM")
                        )
                        await db.commit()

                        print(f"📢 Convocatória COLETIVO enviada (ID {encontro.id})")
                    else:
                        print(f"❌ Falha envio convocatória ({enviados}/{total})")


# ==========================
# MAIN
# ==========================
async def main():
    await monitorar_encontros_coletivo()


if __name__ == "__main__":
    asyncio.run(main())