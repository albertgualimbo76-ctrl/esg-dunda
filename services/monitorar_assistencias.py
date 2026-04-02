import os
import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from database import SessionLocal
from models.assistencia import AssistenciaMutua
from models.contactos_professores import ContactoProfessor

# Intervalo de verificação do loop (em segundos)
INTERVALO_VERIFICACAO = 30  # checa a cada 30 segundos

# ==========================
# Função para enviar SMS via endpoint
# ==========================
async def enviar_sms_api(mensagem, numeros):

    base_url = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:8000")
    url = f"{base_url}/sms/enviar"

    payload = {
        "sender_id": "ESG-DUNDA",
        "mensagem": mensagem,
        "numeros": numeros
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload)
            print(f"Resposta da API SMS: {resp.status_code}, {resp.text}")

            if resp.status_code != 200:
                print(f"⚠️ Erro ao enviar SMS: {resp.text}")

        except Exception as e:
            print(f"⚠️ Exception ao enviar SMS: {e}")


# ==========================
# Monitor de assistências
# ==========================
async def monitorar_assistencias():

    print("🔄 Monitor automático de assistências iniciado")

    while True:

        agora = datetime.now()

        # Calcula o tempo até o início da próxima hora
        proxima_hora = (agora.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        tempo_ate_proxima_hora = (proxima_hora - agora).total_seconds()

        print(f"\n📅 Verificando assistências em {agora}. Próxima verificação às {proxima_hora}")

        # Espera até o início da próxima hora
        await asyncio.sleep(tempo_ate_proxima_hora)

        async with SessionLocal() as db:

            result = await db.execute(
                select(AssistenciaMutua)
                .where(AssistenciaMutua.status_aprovacao == "APROVADO")
            )

            assistencias = result.scalars().all()

            print(f"Assistências encontradas: {len(assistencias)}")

            for a in assistencias:

                print(f"\n🔎 Processando Assistência ID {a.id}")

                data_assistencia = a.data_hora

                # ================================
                # Calcular momento de envio (1 dia antes)
                # ================================
                momento_envio = data_assistencia - timedelta(days=1)

                print(f"Data assistência: {data_assistencia}")
                print(f"Momento envio SMS: {momento_envio}")

                # Se ainda não chegou o momento de enviar
                if agora < momento_envio:
                    print("⏳ Ainda não chegou o momento de enviar SMS")
                    continue

                # Se a assistência já passou
                if agora > data_assistencia:
                    print("⚠️ Assistência já passou. Ignorando.")
                    continue

                # ================================
                # Buscar professor assistido
                # ================================
                result_assistido = await db.execute(
                    select(ContactoProfessor)
                    .where(ContactoProfessor.nome == a.professor_assistido_nome)
                )

                professor_assistido = result_assistido.scalars().first()

                # ================================
                # Buscar professor assistente
                # ================================
                result_assistente = await db.execute(
                    select(ContactoProfessor)
                    .where(ContactoProfessor.nome == a.professor_assistente_nome)
                )

                professor_assistente = result_assistente.scalars().first()

                # ================================
                # Enviar SMS ao professor assistido
                # ================================
                if professor_assistido:

                    numero_assistido = professor_assistido.telefone

                    print(f"📲 Número Assistido: {numero_assistido}")

                    mensagem_assistido = (
                        f"Saudacoes, amanha dia {a.data_hora.strftime('%d/%m/%Y')} "
                        f"tera uma assistencia de aula na disciplina de {a.disciplina} "
                        f"pelas {a.data_hora.strftime('%H:%M')}h, "
                        f"pelo professor {a.professor_assistente_nome}. Bom trabalho."
                    )

                    await enviar_sms_api(
                        mensagem_assistido,
                        [numero_assistido]
                    )

                    await asyncio.sleep(30)

                else:
                    print(f"⚠️ Professor assistido não encontrado: {a.professor_assistido_nome}")

                # ================================
                # Enviar SMS ao professor assistente
                # ================================
                if professor_assistente:

                    numero_assistente = professor_assistente.telefone

                    print(f"📲 Número Assistente: {numero_assistente}")

                    mensagem_assistente = (
                        f"Saudacoes, amanha dia {a.data_hora.strftime('%d/%m/%Y')} "
                        f"pela {a.data_hora.strftime('%H:%M')}h, devera efectuar uma "
                        f"assistencia de aula de {a.disciplina}, na {a.classe} classe, "
                        f"turma {a.turma}, ao professor {a.professor_assistido_nome}, "
                        f"na sala numero {a.numero_sala}."
                    )

                    await enviar_sms_api(
                        mensagem_assistente,
                        [numero_assistente]
                    )

                    await asyncio.sleep(30)

                else:
                    print(f"⚠️ Professor assistente não encontrado: {a.professor_assistente_nome}")

                # ================================
                # Atualizar status para evitar reenvio
                # ================================
                await db.execute(
                    update(AssistenciaMutua)
                    .where(AssistenciaMutua.id == a.id)
                    .values(status_aprovacao="NAO")
                )

                await db.commit()

                print(f"✅ SMS enviado e status atualizado para NAO (ID {a.id})")

        # Espera próximo ciclo até o início da próxima hora
        await asyncio.sleep(tempo_ate_proxima_hora)


# ==========================
# Inicia monitor
# ==========================
async def main():

    await monitorar_assistencias()


if __name__ == "__main__":

    asyncio.run(main())