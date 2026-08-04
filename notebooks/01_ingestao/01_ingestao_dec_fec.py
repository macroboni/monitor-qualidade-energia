# Databricks notebook source
# Projeto: Monitor de Qualidade de Energia
# Etapa: Ingestão dos dados DEC e FEC da ANEEL

import sys
from pathlib import Path


def localizar_raiz_projeto() -> Path:
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


from src.ingestion.aneel_dec_fec import (
    baixar_arquivo,
    criar_estrutura_armazenamento,
    filtrar_dec_fec,
    ler_csv,
    salvar_e_extrair_arquivo,
    validar_arquivo_csv,
)


print("Iniciando ingestão DEC/FEC.")

conteudo_download = baixar_arquivo()

criar_estrutura_armazenamento(spark)

salvar_e_extrair_arquivo(conteudo_download)

validar_arquivo_csv()

df_dec_fec = ler_csv(spark)

df_dec_fec_principal = filtrar_dec_fec(df_dec_fec)

print("Schema do arquivo:")
df_dec_fec.printSchema()

print("Primeiros cinco registros:")
df_dec_fec.show(5, truncate=False)

print("Quantidade de registros DEC e FEC:")

(
    df_dec_fec_principal
    .groupBy("SigIndicador")
    .count()
    .orderBy("SigIndicador")
    .show()
)

print("Ingestão finalizada com sucesso.")