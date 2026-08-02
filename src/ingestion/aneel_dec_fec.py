import io
import os
import zipfile
from pathlib import Path
from shutil import copyfileobj

import requests
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from src.config import (
    CAMINHO_CSV,
    CAMINHO_ZIP,
    CATALOGO,
    PASTA_VOLUME_DEC_FEC,
    SCHEMA,
    URL_DEC_FEC,
    VOLUME,
)


def baixar_arquivo() -> bytes:
    """Baixa o arquivo compactado da ANEEL."""

    print("Baixando arquivo da ANEEL...")

    resposta = requests.get(
        URL_DEC_FEC,
        timeout=180,
    )

    resposta.raise_for_status()

    print("Status:", resposta.status_code)
    print("Tipo informado:", resposta.headers.get("content-type"))
    print("Tamanho:", len(resposta.content), "bytes")

    return resposta.content


def criar_estrutura_armazenamento(
    spark: SparkSession,
) -> None:
    """Cria o schema, o Volume e a pasta do projeto."""

    spark.sql(f"""
        CREATE SCHEMA IF NOT EXISTS {CATALOGO}.{SCHEMA}
        COMMENT 'Objetos do projeto Monitor de Qualidade de Energia'
    """)

    spark.sql(f"""
        CREATE VOLUME IF NOT EXISTS {CATALOGO}.{SCHEMA}.{VOLUME}
        COMMENT 'Arquivos brutos baixados do portal da ANEEL'
    """)

    Path(PASTA_VOLUME_DEC_FEC).mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Estrutura de armazenamento criada.")


def salvar_e_extrair_arquivo(
    conteudo_download: bytes,
) -> None:
    """Salva o ZIP original e extrai o CSV para o Volume."""

    with open(CAMINHO_ZIP, "wb") as destino_zip:
        destino_zip.write(conteudo_download)

    buffer_zip = io.BytesIO(conteudo_download)

    if not zipfile.is_zipfile(buffer_zip):
        raise ValueError(
            "O arquivo baixado não foi reconhecido como ZIP."
        )

    buffer_zip.seek(0)

    with zipfile.ZipFile(buffer_zip) as arquivo_zip:
        arquivos_csv = [
            nome
            for nome in arquivo_zip.namelist()
            if nome.lower().endswith(".csv")
        ]

        if not arquivos_csv:
            raise ValueError(
                "Nenhum arquivo CSV foi encontrado dentro do ZIP."
            )

        with arquivo_zip.open(arquivos_csv[0]) as origem:
            with open(CAMINHO_CSV, "wb") as destino:
                copyfileobj(origem, destino)

    print("CSV extraído para:", CAMINHO_CSV)


def validar_arquivo_csv() -> None:
    """Verifica se o CSV existe e possui conteúdo."""

    if not os.path.exists(CAMINHO_CSV):
        raise FileNotFoundError(
            f"Arquivo CSV não encontrado: {CAMINHO_CSV}"
        )

    tamanho = os.path.getsize(CAMINHO_CSV)

    if tamanho == 0:
        raise ValueError(
            f"Arquivo CSV está vazio: {CAMINHO_CSV}"
        )

    print(f"Arquivo CSV localizado: {tamanho:,} bytes")


def ler_csv(
    spark: SparkSession,
) -> DataFrame:
    """Lê o CSV extraído usando Spark."""

    return (
        spark.read
        .option("header", True)
        .option("sep", ";")
        .option("quote", "\"")
        .option("escape", "\"")
        .option("encoding", "UTF-8")
        .csv(CAMINHO_CSV)
    )


def filtrar_dec_fec(
    dataframe: DataFrame,
) -> DataFrame:
    """Mantém somente os indicadores principais DEC e FEC."""

    return dataframe.filter(
        F.col("SigIndicador").isin("DEC", "FEC")
    )