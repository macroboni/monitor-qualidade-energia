# Teste das importações do projeto

import sys
from pathlib import Path


def localizar_raiz_projeto() -> Path:
    """Procura a pasta raiz que contém o diretório src."""

    diretorio_atual = Path.cwd().resolve()

    for candidato in [diretorio_atual, *diretorio_atual.parents]:
        if (candidato / "src").is_dir():
            return candidato

    raise FileNotFoundError(
        "Não foi possível localizar a raiz do projeto."
    )


RAIZ_PROJETO = localizar_raiz_projeto()

if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


from src.config import (
    CAMINHO_CSV,
    CAMINHO_ZIP,
    URL_DEC_FEC,
)

from src.ingestion.aneel_dec_fec import (
    baixar_arquivo,
    criar_estrutura_armazenamento,
    filtrar_dec_fec,
    ler_csv,
    salvar_e_extrair_arquivo,
    validar_arquivo_csv,
)


print("Importações realizadas com sucesso.")
print("Raiz do projeto:", RAIZ_PROJETO)
print("URL:", URL_DEC_FEC)
print("ZIP:", CAMINHO_ZIP)
print("CSV:", CAMINHO_CSV)