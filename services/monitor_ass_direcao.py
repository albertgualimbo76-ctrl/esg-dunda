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
# 📩 Função para enviar SMS via endpoint
# ==========================
async def enviar_sms_api(mensagem, numeros):
    base_url = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:8000")
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
                print(f"✅ SMS enviado: {numeros}")
                return True
            else:
                print(f"❌ Erro SMS: {resp.text}")
                return False
        except Exception as e:
            print(f"⚠️ Erro ao enviar SMS: {e}")
            return False


# ==========================
# 🔄 EXECUÇÃO ÚNICA (SEM WHILE TRUE)
# ==========================
async def monitorar_assistencias_direcao():
    print("🔄 Execução única de assistências de direção iniciada")

    agora = datetime.now()

    async with SessionLocal() as db:

        result = await db.execute(
            select(AssistenciaDirecao)
            .where(AssistenciaDirecao.status_aprovacao == "APROVADO")
        )
        assistencias = result.scalars().all()

        print(f"\n📅 Execução em {agora}")
        print(f"📊 Assistências encontradas: {len(assistencias)}")

        for a in assistencias:

            data_assistencia = a.data_hora

            if agora >= data_assistencia:
                print(f"⚠️ Assistência já passou (ID {a.id})")
                continue

            momento_envio = data_assistencia - timedelta(days=1)

            # ==========================
            # Professor assistido
            # ==========================
            result_prof = await db.execute(
                select(ContactoProfessor)
                .where(ContactoProfessor.nome == a.professor_assistido_nome)
            )
            professor_assistido = result_prof.scalars().first()

            # ==========================
            # Diretor assistente
            # ==========================
            result_dir = await db.execute(
                select(ContactoDiretor)
                .where(ContactoDiretor.nome == a.diretor_assistente_nome)
            )
            diretor_assistente = result_dir.scalars().first()

            # ==========================
            # ENVIO SMS
            # ==========================
            if agora >= momento_envio:

                if professor_assistido:
                    mensagem_prof = (
                        f"Saudacoes, amanha dia {a.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h "
                        f"tera uma assistencia de aula na disciplina de {a.disciplina} "
                        f"as {a.data_hora.strftime('%H:%M')}h, pelo membro da direcao "
                        f"{a.diretor_assistente_nome}. Bom trabalho."
                    )

                    await enviar_sms_api(mensagem_prof, [professor_assistido.telefone])
                    await asyncio.sleep(5)

                if diretor_assistente:
                    mensagem_dir = (
                        f"Saudacoes, amanha {a.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h "
                        f"devera assistir a aula de {a.disciplina} da {a.classe} classe, "
                        f"turma {a.turma}, ao professor {a.professor_assistido_nome}, "
                        f"na sala {a.numero_sala}."
                    )

                    await enviar_sms_api(mensagem_dir, [diretor_assistente.telefone])
                    await asyncio.sleep(5)

                # ==========================
                # Atualizar status
                # ==========================
                await db.execute(
                    update(AssistenciaDirecao)
                    .where(AssistenciaDirecao.id == a.id)
                    .values(status_aprovacao="NAO")
                )
                await db.commit()

                print(f"✅ Status atualizado (ID {a.id})")


# ==========================
# MAIN
# ==========================
async def main():
    await monitorar_assistencias_direcao()


if __name__ == "__main__":
    asyncio.run(main())