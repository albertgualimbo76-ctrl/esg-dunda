import re
import unicodedata

def normalizar_username(nome: str) -> str:
    # remove acentos
    nome = unicodedata.normalize("NFKD", nome)
    nome = nome.encode("ASCII", "ignore").decode("ASCII")

    # minusculas
    nome = nome.lower()

    # remove tudo que não for letra ou número
    nome = re.sub(r"[^a-z0-9]", "", nome)

    return nome
