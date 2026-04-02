import os
import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from database import SessionLocal
from models.assistencia_direcao import AssistenciaDirecao
from models.contactos_professores import ContactoProfessor
from models.contactos_diretor import ContactoDiretor

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
# Monitor de assistências de direção
# ==========================
async def monitorar_assistencias_direcao():

    print("🔄 Monitor automático de assistências de direção iniciado")

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
                select(AssistenciaDirecao)
                .where(AssistenciaDirecao.status_aprovacao == "APROVADO")
            )

            assistencias = result.scalars().all()

            print(f"Assistências encontradas: {len(assistencias)}")

            for a in assistencias:

                data_assistencia = a.data_hora

                # Momento em que o SMS deve ser enviado (1 dia antes)
                momento_envio = data_assistencia - timedelta(days=1)

                print(f"\n🔎 Assistência ID {a.id}")
                print(f"Data da assistência: {data_assistencia}")
                print(f"Momento do envio: {momento_envio}")

                # Se ainda não chegou o momento de enviar
                if agora < momento_envio:
                    print("⏳ Ainda não chegou a hora de enviar SMS")
                    continue

                # Se a assistência já passou
                if agora > data_assistencia:
                    print("⚠️ Assistência já passou")
                    continue

                print("🔔 Enviando lembretes...")

                # ==========================
                # Buscar professor assistido
                # ==========================
                result_assistido = await db.execute(
                    select(ContactoProfessor)
                    .where(ContactoProfessor.nome == a.professor_assistido_nome)
                )

                professor_assistido = result_assistido.scalars().first()

                # ==========================
                # Buscar diretor assistente
                # ==========================
                result_diretor = await db.execute(
                    select(ContactoDiretor)
                    .where(ContactoDiretor.nome == a.diretor_assistente_nome)
                )

                diretor_assistente = result_diretor.scalars().first()

                # ==========================
                # Enviar SMS ao professor assistido
                # ==========================
                if professor_assistido:

                    numero_assistido = professor_assistido.telefone

                    mensagem_assistido = (
                        f"Saudacoes, amanha ({a.data_hora.strftime('%d/%m/%Y')}) "
                        f"tera uma assistencia de aula da disciplina de {a.disciplina} "
                        f"as {a.data_hora.strftime('%H:%M')}h, pelo membro da direcao "
                        f"{a.diretor_assistente_nome}. Bom trabalho."
                    )

                    await enviar_sms_api(
                        mensagem_assistido,
                        [numero_assistido]
                    )

                    print(f"✅ SMS enviado ao professor assistido: {numero_assistido}")

                    await asyncio.sleep(30)

                else:
                    print(f"⚠️ Professor assistido não encontrado: {a.professor_assistido_nome}")

                # ==========================
                # Enviar SMS ao diretor assistente
                # ==========================
                if diretor_assistente:

                    numero_diretor = diretor_assistente.telefone

                    mensagem_diretor = (
                        f"Saudacoes, amanha ({a.data_hora.strftime('%d/%m/%Y')}) "
                        f"devera assistir a aula de {a.disciplina} da {a.classe} classe, "
                        f"turma {a.turma}, ao professor {a.professor_assistido_nome}, "
                        f"na sala {a.numero_sala}."
                    )

                    await enviar_sms_api(
                        mensagem_diretor,
                        [numero_diretor]
                    )

                    print(f"✅ SMS enviado ao diretor assistente: {numero_diretor}")

                    await asyncio.sleep(30)

                else:
                    print(f"⚠️ Diretor assistente não encontrado: {a.diretor_assistente_nome}")

                # ==========================
                # Atualizar status para evitar reenvio
                # ==========================
                await db.execute(
                    update(AssistenciaDirecao)
                    .where(AssistenciaDirecao.id == a.id)
                    .values(status_aprovacao="NAO")
                )

                await db.commit()

                print(f"✅ Status atualizado para NAO (Assistência ID {a.id})")

        # Espera próximo ciclo
        await asyncio.sleep(tempo_ate_proxima_hora)


# ==========================
# Inicializa o monitor
# ==========================
async def main():

    await monitorar_assistencias_direcao()


if __name__ == "__main__":

    asyncio.run(main())