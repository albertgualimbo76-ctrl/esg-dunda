import os
import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from database import SessionLocal
from models.assistencia import AssistenciaMutua
from models.contactos_professores import ContactoProfessor


# ==========================
# 📩 Função para enviar SMS via endpoint
# ==========================
async def enviar_sms_api(mensagem, numeros):
    """
    Envia SMS usando endpoint /sms/enviar
    Aceita número único ou lista de números
    """
    if not isinstance(numeros, list):
        numeros = [numeros]

    base_url = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:8000")
    url = f"{base_url}/sms/enviar"

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
            print(f"⚠️ Exception ao enviar SMS: {e}")
            return False


# ==========================
# 🔄 EXECUÇÃO ÚNICA (SEM WHILE TRUE)
# ==========================
async def monitorar_assistencias():
    print("🔄 Execução única de assistências iniciada")

    agora = datetime.now()

    async with SessionLocal() as db:
        result = await db.execute(
            select(AssistenciaMutua)
            .where(AssistenciaMutua.status_aprovacao == "APROVADO")
        )

        assistencias = result.scalars().all()

        print(f"\n📅 Execução em: {agora}")
        print(f"📊 Assistências encontradas: {len(assistencias)}")

        for a in assistencias:

            data_assistencia = a.data_hora

            # ❌ Se já passou, ignora
            if agora >= data_assistencia:
                print(f"⚠️ Assistência já passou (ID {a.id})")
                continue

            # ==========================
            # Buscar professor assistido
            # ==========================
            result_assistido = await db.execute(
                select(ContactoProfessor)
                .where(ContactoProfessor.nome == a.professor_assistido_nome)
            )
            professor_assistido = result_assistido.scalars().first()

            # ==========================
            # Buscar professor assistente
            # ==========================
            result_assistente = await db.execute(
                select(ContactoProfessor)
                .where(ContactoProfessor.nome == a.professor_assistente_nome)
            )
            professor_assistente = result_assistente.scalars().first()

            # ==========================
            # Enviar SMS
            # ==========================
            if professor_assistido:
                mensagem_assistido = (
                    f"Saudacoes, amanha dia {a.data_hora.strftime('%d/%m/%Y')} "
                    f"tera uma assistencia de aula na disciplina de {a.disciplina} "
                    f"pelas {a.data_hora.strftime('%H:%M')}h, "
                    f"pelo(a) professor(a) {a.professor_assistente_nome}. Bom trabalho."
                )

                await enviar_sms_api(mensagem_assistido, [professor_assistido.telefone])
                await asyncio.sleep(5)

            if professor_assistente:
                mensagem_assistente = (
                    f"Saudacoes, amanha dia {a.data_hora.strftime('%d/%m/%Y')} "
                    f"pela {a.data_hora.strftime('%H:%M')}h, devera efectuar uma "
                    f"assistencia de aula de {a.disciplina}, na {a.classe} classe, "
                    f"turma {a.turma}, a(o) professor(a) {a.professor_assistido_nome}, "
                    f"na sala numero {a.numero_sala}."
                )

                await enviar_sms_api(mensagem_assistente, [professor_assistente.telefone])
                await asyncio.sleep(5)

            # ==========================
            # Atualiza status
            # ==========================
            await db.execute(
                update(AssistenciaMutua)
                .where(AssistenciaMutua.id == a.id)
                .values(status_aprovacao="NAO")
            )

            await db.commit()

            print(f"✅ Processado e atualizado (ID {a.id})")


# ==========================
# MAIN
# ==========================
async def main():
    await monitorar_assistencias()


if __name__ == "__main__":
    asyncio.run(main())