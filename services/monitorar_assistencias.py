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
        "numeros": numeros  # Aqui garantimos que é uma lista de números
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
        print(f"Verificando assistências para o dia: {agora.date()}")

        async with SessionLocal() as db:
            # Ajuste da consulta para considerar apenas a data sem a hora
            dia_atual = agora.date()

            # Seleciona todas assistências com status 'APROVADO' e data de assistência do dia ou no futuro
            result = await db.execute(
                select(AssistenciaMutua)
                .where(
                    AssistenciaMutua.status_aprovacao == "APROVADO",  # Filtra as assistências aprovadas
                    AssistenciaMutua.data_hora >= datetime.combine(dia_atual, datetime.min.time())  # A data da assistência deve ser maior ou igual à data de hoje
                )
            )
            assistencias = result.scalars().all()

            # Depuração: exibe as datas de assistências
            print(f"Assistências encontradas: {len(assistencias)}")
            for a in assistencias:
                print(f"Assistência ID {a.id}: {a.professor_assistido_nome} - {a.professor_assistente_nome}")
                print(f"Data e Hora da Assistência: {a.data_hora}")

            if not assistencias:
                print(f"⏸️ Nenhuma assistência aprovada encontrada para hoje ou no passado.")

            for a in assistencias:
                print(f"🔎 Processando Assistência ID {a.id}: {a.professor_assistido_nome} - {a.professor_assistente_nome}")

                # Verificar se a data da assistência já passou
                if a.data_hora <= agora:
                    print(f"📅 A data da assistência ({a.data_hora}) já passou. Ignorando envio de SMS para esta assistência.")
                    continue  # Não enviar SMS se a data já passou

                # Pegar contatos do professor assistido com base no nome
                result_assistido = await db.execute(
                    select(ContactoProfessor)
                    .where(ContactoProfessor.nome == a.professor_assistido_nome)
                )
                professor_assistido = result_assistido.scalars().first()

                # Pegar contatos do professor assistente com base no nome
                result_assistente = await db.execute(
                    select(ContactoProfessor)
                    .where(ContactoProfessor.nome == a.professor_assistente_nome)
                )
                professor_assistente = result_assistente.scalars().first()

                # ==========================
                # Verificar se o professor assistido foi encontrado
                # ==========================
                if professor_assistido:
                    print(f"📲 Número do Professor Assistido: {professor_assistido.telefone}")
                    mensagem_assistido = (
                        f"Saudacoes, amanha dia {a.data_hora.strftime('%d/%m/%Y')} tera uma assistencia de aula na disciplina de {a.disciplina} pelas {a.data_hora.strftime('%H:%M')}h, pelo professor {a.professor_assistente_nome}. Bom trabalho."
                    )
                    print(f"Enviando para: {professor_assistido.telefone}")
                    await enviar_sms_api(mensagem_assistido,
                                         [professor_assistido.telefone])  # Envia para um número de cada vez
                    await asyncio.sleep(30)  # Pausa de 30 segundos entre os envios
                else:
                    print(f"⚠️ Não foi encontrado o professor assistido: {a.professor_assistido_nome}")

                # ==========================
                # Verificar se o professor assistente foi encontrado
                # ==========================
                if professor_assistente:
                    print(f"📲 Número do Professor Assistente: {professor_assistente.telefone}")
                    mensagem_assistente = (
                        f"Saudacoes, amanha dia {a.data_hora.strftime('%d/%m/%Y')} pela {a.data_hora.strftime('%H:%M')}h, devera efectuar uma assistencia de aula de {a.disciplina}, na {a.classe} classe, turma {a.turma}, ao professor {a.professor_assistido_nome}, na sala numero {a.numero_sala}."
                    )
                    print(f"Enviando para: {professor_assistente.telefone}")
                    await enviar_sms_api(mensagem_assistente,
                                         [professor_assistente.telefone])  # Envia para um número de cada vez
                    await asyncio.sleep(30)  # Pausa de 30 segundos entre os envios
                else:
                    print(f"⚠️ Não foi encontrado o professor assistente: {a.professor_assistente_nome}")

                # ==========================
                # Atualiza o status para NAO para não enviar novamente
                # ==========================
                await db.execute(
                    update(AssistenciaMutua)
                    .where(AssistenciaMutua.id == a.id)
                    .values(status_aprovacao="NAO")
                )
                await db.commit()
                print(f"✅ Lembrete enviado e status atualizado para NAO (Assistência ID {a.id})")

        # Espera próximo loop
        await asyncio.sleep(INTERVALO_VERIFICACAO)


# Inicia a verificação de assistências
async def main():
    await monitorar_assistencias()


if __name__ == "__main__":
    asyncio.run(main())