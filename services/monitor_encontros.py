import os
import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from database import SessionLocal
from models.encontro import Encontro
from routers.contactos import tipo_tabela

# Intervalo de verificação do loop (em segundos)
INTERVALO_VERIFICACAO = 30


# ==========================
# 📩 Envio de SMS usando endpoint
# ==========================
async def enviar_sms_api(mensagem, numeros):

    base_url = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:8000")
    url = f"{base_url}/sms/enviar"

    # Garantir que é lista
    if not isinstance(numeros, list):
        numeros = [numeros]

    payload = {
        "mensagem": mensagem,
        "numeros": numeros
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(url, json=payload)

            if resp.status_code == 200:
                return True
            else:
                print("❌ Erro API:", resp.text)
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

        print(f"📞 Números encontrados para {tipo}: {numeros}")

        return numeros


# ==========================
# 🔄 Monitor automático
# ==========================
async def monitorar_encontros():

    print("🔄 Monitor automático de encontros iniciado")

    while True:

        agora = datetime.now()

        # Calcula o tempo até o início da próxima hora
        proxima_hora = (agora.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        tempo_ate_proxima_hora = (proxima_hora - agora).total_seconds()

        print(f"\n📅 Verificando encontros em {agora}. Próxima verificação às {proxima_hora}")

        # Espera até o início da próxima hora
        await asyncio.sleep(tempo_ate_proxima_hora)

        async with SessionLocal() as db:

            result = await db.execute(
                select(Encontro).where(Encontro.status == "APROVADO")
            )

            encontros = result.scalars().all()

            for encontro in encontros:

                # ==================================================
                # 🔔 ALERTA (2 dias antes)
                # ==================================================
                momento_alerta = encontro.data_hora - timedelta(days=2)

                if encontro.alerta_enviado == "NAO" and agora >= momento_alerta:

                    if encontro.tipo == "PROFESSORES":
                        numeros_alerta = await pegar_numeros("diretor")

                    elif encontro.tipo == "FUNCIONARIOS":
                        numeros_alerta = await pegar_numeros("direcao")

                    else:
                        continue

                    if numeros_alerta:

                        mensagem_alerta = (
                            f"Saudacoes, ha um encontro referente a "
                            f"{encontro.titulo}, agendado para "
                            f"{encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h. "
                            f"Se pretende adiar ou cancelar, entre no sistema. "
                            f"Enviado por sistema."
                        )

                        enviados = 0
                        total = len(numeros_alerta)

                        print(f"\n🔔 ALERTA Encontro {encontro.id}")
                        print(f"📊 Total de números: {total}")

                        for numero in numeros_alerta:

                            print(f"📤 Enviando alerta para {numero}...")

                            sucesso = await enviar_sms_api(
                                mensagem_alerta,
                                numero
                            )

                            if sucesso:
                                enviados += 1
                                print(f"✅ Enviado para {numero}")
                            else:
                                print(f"❌ Falha para {numero}")

                            await asyncio.sleep(5)

                        print(f"📊 Resultado ALERTA: {enviados}/{total}")

                        if total > 0 and enviados == total:

                            await db.execute(
                                update(Encontro)
                                .where(Encontro.id == encontro.id)
                                .values(alerta_enviado="SIM")
                            )
                            await db.commit()

                            print(f"✅ Alerta marcado como SIM (Encontro {encontro.id})")
                        else:
                            print("⚠️ Nem todos alertas foram enviados")


                # ==================================================
                # 📢 CONVOCATÓRIA (1 dia antes)
                # ==================================================
                momento_convocatoria = encontro.data_hora - timedelta(days=1)

                if encontro.convocatoria_enviada == "NAO" and agora >= momento_convocatoria:

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

                    enviados = 0
                    total = len(numeros_convocatoria)

                    print(f"\n📢 CONVOCATÓRIA Encontro {encontro.id}")
                    print(f"📊 Total de números: {total}")

                    for numero in numeros_convocatoria:

                        print(f"📤 Enviando convocatória para {numero}...")

                        sucesso = await enviar_sms_api(
                            mensagem_convocatoria,
                            numero
                        )

                        if sucesso:
                            enviados += 1
                            print(f"✅ Enviado para {numero}")
                        else:
                            print(f"❌ Falha para {numero}")

                        await asyncio.sleep(5)

                    print(f"📊 Resultado CONVOCATÓRIA: {enviados}/{total}")

                    if total > 0 and enviados == total:

                        await db.execute(
                            update(Encontro)
                            .where(Encontro.id == encontro.id)
                            .values(convocatoria_enviada="SIM")
                        )
                        await db.commit()

                        print(f"📢 Convocatória marcada como SIM (Encontro {encontro.id})")
                    else:
                        print("⚠️ Nem todos SMS foram enviados")

        # Espera próximo ciclo até o início da próxima hora
        await asyncio.sleep(tempo_ate_proxima_hora)


# ==========================
# Inicializa o monitor
# ==========================
async def main():

    await monitorar_encontros()


if __name__ == "__main__":

    asyncio.run(main())