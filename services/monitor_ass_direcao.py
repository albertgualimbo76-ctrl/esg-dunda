import os
import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from database import SessionLocal
from models.assistencia_direcao import AssistenciaDirecao
from models.contactos_professores import ContactoProfessor
from models.contactos_diretor import ContactoDiretor

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
        "numeros": numeros  # lista de números
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
        print(f"Verificando assistências para envio de lembrete (um dia antes)...")

        async with SessionLocal() as db:
            # Seleciona apenas assistências aprovadas
            result = await db.execute(
                select(AssistenciaDirecao)
                .where(AssistenciaDirecao.status_aprovacao == "APROVADO")
            )
            assistencias = result.scalars().all()

            print(f"Assistências encontradas: {len(assistencias)}")
            for a in assistencias:
                # Calcula um dia antes da data da assistência
                lembrete_data = a.data_hora - timedelta(days=1)
                if lembrete_data.date() != agora.date():
                    continue  # Envia apenas se for um dia antes

                print(f"🔔 Preparando lembrete para Assistência ID {a.id} no dia {a.data_hora}")

                # Pegar contatos do professor assistido
                result_assistido = await db.execute(
                    select(ContactoProfessor)
                    .where(ContactoProfessor.nome == a.professor_assistido_nome)
                )
                professor_assistido = result_assistido.scalars().first()

                # Pegar contatos do diretor assistente
                result_diretor = await db.execute(
                    select(ContactoDiretor)
                    .where(ContactoDiretor.nome == a.diretor_assistente_nome)
                )
                diretor_assistente = result_diretor.scalars().first()

                # ==========================
                # Envia SMS para professor assistido
                # ==========================
                if professor_assistido:
                    mensagem_assistido = (
                        f"Saudacoes, amanha ({a.data_hora.strftime('%d/%m/%Y')}) "
                        f"tera uma assistencia de aula da disciplina de {a.disciplina} "
                        f"as {a.data_hora.strftime('%H:%M')}h, pelo membro da direcao {a.diretor_assistente_nome}. Bom trabalho."
                    )
                    await enviar_sms_api(mensagem_assistido, [professor_assistido.telefone])
                    print(f"✅ SMS enviado ao professor assistido: {professor_assistido.telefone}")
                else:
                    print(f"⚠️ Professor assistido não encontrado: {a.professor_assistido_nome}")

                # ==========================
                # Envia SMS para diretor assistente
                # ==========================
                if diretor_assistente:
                    mensagem_diretor = (
                        f"Saudacoes, amanha ({a.data_hora.strftime('%d/%m/%Y')}) "
                        f"devera assistir a aula de {a.disciplina} da {a.classe} classe,"
                        f"turma {a.turma}, ao o professor {a.professor_assistido_nome}, "
                        f"na sala {a.numero_sala}"
                    )
                    await enviar_sms_api(mensagem_diretor, [diretor_assistente.telefone])
                    print(f"✅ SMS enviado ao diretor assistente: {diretor_assistente.telefone}")
                else:
                    print(f"⚠️ Diretor assistente não encontrado: {a.diretor_assistente_nome}")

                # ==========================
                # Atualiza o status para NAO para não enviar novamente
                # ==========================
                await db.execute(
                    update(AssistenciaDirecao)
                    .where(AssistenciaDirecao.id == a.id)
                    .values(status_aprovacao="NAO")
                )
                await db.commit()
                print(f"✅ Status atualizado para NAO (Assistência ID {a.id})")

        # Espera próximo loop
        await asyncio.sleep(INTERVALO_VERIFICACAO)

# ==========================
# Inicializa o monitor
# ==========================
async def main():
    await monitorar_assistencias_direcao()

if __name__ == "__main__":
    asyncio.run(main())
