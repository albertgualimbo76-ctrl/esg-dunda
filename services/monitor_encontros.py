import os
import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from database import SessionLocal
from models.encontro import Encontro
from routers.contactos import tipo_tabela


# ========================
# 📩 Envio de SMS usando endpoint
# ========================
async def enviar_sms_api(mensagem, numeros):
    base_url = os.getenv("RENDER_EXTERNAL_URL")
    if not base_url:
        base_url = "http://127.0.0.1:8000"

    url = f"{base_url}/sms/enviar"

    if not isinstance(numeros, list):
        numeros = [numeros]

    payload = {
        "sender_id": "ESG-DUNDA",
        "mensagem": mensagem,
        "numeros": numeros
    }

    print("📡 URL:", url)
    print("📤 Enviando para:", numeros)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(url, json=payload)

            print("📥 Status:", resp.status_code)
            print("📥 Resposta:", resp.text)

            if resp.status_code == 200:
                print("✅ SMS enviado com sucesso")
                return True
            else:
                print("❌ Erro no envio")
                return False

        except Exception as e:
            print(f"⚠️ Exception ao enviar SMS: {e}")
            return False


# ==========================
# 📞 Pegar números
# ==========================
async def pegar_numeros(tipo):
    if tipo not in tipo_tabela:
        return []

    Model = tipo_tabela[tipo]

    async with SessionLocal() as db:
        result = await db.execute(select(Model))
        contactos = result.scalars().all()

        numeros = [c.telefone for c in contactos if c.telefone]

        print(f"\n📞 [LOG] Tipo: {tipo}")
        print(f"📞 [LOG] Quantidade: {len(numeros)}")
        print(f"📞 [LOG] Números: {numeros}\n")

        return numeros


# ==========================
# 🔄 Monitor automático
# ==========================
async def monitorar_encontros():
    print("🔄 Monitor automático de encontros iniciado")

    while True:
        agora = datetime.now()

        print(f"\n📅 Verificando encontros em {agora}")

        async with SessionLocal() as db:
            result = await db.execute(
                select(Encontro).where(Encontro.status == "APROVADO")
            )
            encontros = result.scalars().all()

            for encontro in encontros:
                # ==========================
                # 🔔 ALERTA (2 dias antes)
                # ==========================
                momento_alerta = encontro.data_hora - timedelta(days=2)

                if encontro.alerta_enviado == "NAO" and agora >= momento_alerta:
                    print(f"\n🔔 Enviando ALERTA para encontro {encontro.id}")

                    if encontro.tipo == "PROFESSORES":
                        numeros_alerta = await pegar_numeros("diretor")
                    elif encontro.tipo == "FUNCIONARIOS":
                        numeros_alerta = await pegar_numeros("direcao")
                    else:
                        continue

                    if numeros_alerta:
                        print("📤 [ALERTA] Números destino:", numeros_alerta)

                        mensagem_alerta = (
                            f"Saudacoes, ha um encontro referente a "
                            f"{encontro.titulo}, agendado para "
                            f"{encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h. "
                            f"Se pretende adiar ou cancelar, entre no sistema."
                        )

                        sucesso = await enviar_sms_api(
                            mensagem_alerta,
                            numeros_alerta
                        )

                        if sucesso:
                            await db.execute(
                                update(Encontro)
                                .where(Encontro.id == encontro.id)
                                .values(alerta_enviado="SIM")
                            )
                            await db.commit()

                            print(f"✅ Alerta marcado como SIM (Encontro {encontro.id})")
                        else:
                            print(f"❌ Falha no envio do alerta {encontro.id}")

                # ==========================
                # 📢 CONVOCATÓRIA (1 dia antes)
                # ==========================
                momento_convocatoria = encontro.data_hora - timedelta(days=1)

                if encontro.convocatoria_enviada == "NAO" and agora >= momento_convocatoria:
                    print(f"\n📢 Enviando CONVOCATÓRIA para encontro {encontro.id}")

                    if encontro.tipo == "PROFESSORES":
                        numeros_convocatoria = await pegar_numeros("professores")
                        mensagem_convocatoria = (
                            f"Saudacoes prezados colegas, a direccao da ESG 1 e 2 de Dunda "
                            f"convoca todos os professores para reuniao referente a "
                            f"{encontro.titulo}, amanha dia "
                            f"{encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h, "
                            f"na sala de reuniao. Pede-se pontualidade. "
                            f"Do: Sector Pedagogico"
                        )

                    elif encontro.tipo == "FUNCIONARIOS":
                        numeros_convocatoria = await pegar_numeros("funcionarios")
                        mensagem_convocatoria = (
                            f"Saudacoes, a direccao da ESG 1 e 2 de Dunda convoca todos os "
                            f"funcionarios para reuniao referente a {encontro.titulo}, "
                            f"amanha dia "
                            f"{encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h, "
                            f"na sala de reuniao. Pede-se pontualidade. "
                            f"DE: Alberto Luis Gualimbo"
                        )
                    else:
                        continue

                    print("📤 [CONVOCATORIA] Números destino:", numeros_convocatoria)

                    enviados = 0
                    total = len(numeros_convocatoria)

                    for numero in numeros_convocatoria:
                        sucesso = await enviar_sms_api(
                            mensagem_convocatoria,
                            numero
                        )

                        if sucesso:
                            enviados += 1

                        await asyncio.sleep(5)

                    if total > 0 and enviados == total:
                        await db.execute(
                            update(Encontro)
                            .where(Encontro.id == encontro.id)
                            .values(convocatoria_enviada="SIM")
                        )
                        await db.commit()

                        print(f"📢 Convocatória marcada como SIM (Encontro {encontro.id})")
                    else:
                        print(f"❌ Nem todos SMS foram enviados ({enviados}/{total})")

        # ⏱️ Espera 60 segundos (mais confiável que 1 hora)
        await asyncio.sleep(3600)


# =====================
# Inicializa
# =====================
async def main():
    await monitorar_encontros()


if __name__ == "__main__":
    asyncio.run(main())
