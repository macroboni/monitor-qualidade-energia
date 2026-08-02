# Databricks notebook source
# Projeto: Monitor de Qualidade de Energia
# Etapa: Ingestão dos dados DEC e FEC da ANEEL

import io
import os
import zipfile
from pathlib import Path
from shutil import copyfileobj

import requests


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

URL_DEC_FEC = (
    "https://dadosabertos.aneel.gov.br/dataset/"
    "d5f0712e-62f6-4736-8dff-9991f10758a7/resource/"
    "4493985c-baea-429c-9df5-3030422c71d7/download/"
    "indicadores-continuidade-coletivos-2020-2029.zip"
)

CATALOGO = "workspace"
SCHEMA = "monitor_energia"
VOLUME = "arquivos_aneel"

PASTA_VOLUME_DEC_FEC = (
    f"/Volumes/{CATALOGO}/{SCHEMA}/{VOLUME}/dec_fec"
)

CAMINHO_ZIP = (
    f"{PASTA_VOLUME_DEC_FEC}/"
    "indicadores_continuidade_coletivos_2020_2029.zip"
)

CAMINHO_CSV = (
    f"{PASTA_VOLUME_DEC_FEC}/"
    "indicadores_continuidade_coletivos_2020_2029.csv"
)


# ============================================================
# 2. BAIXAR O ARQUIVO DA ANEEL
# ============================================================

print("Baixando arquivo da ANEEL...")

resposta_dec_fec = requests.get(
    URL_DEC_FEC,
    timeout=180
)

resposta_dec_fec.raise_for_status()

conteudo_download = resposta_dec_fec.content

print("Status:", resposta_dec_fec.status_code)
print("Tipo informado:", resposta_dec_fec.headers.get("content-type"))
print("Tamanho:", len(conteudo_download), "bytes")


# ============================================================
# 3. CRIAR SCHEMA E VOLUME
# ============================================================

spark.sql(f"""
    CREATE SCHEMA IF NOT EXISTS {CATALOGO}.{SCHEMA}
    COMMENT 'Objetos do projeto Monitor de Qualidade de Energia'
""")

print("Schema criado ou já existente.")

spark.sql(f"""
    CREATE VOLUME IF NOT EXISTS {CATALOGO}.{SCHEMA}.{VOLUME}
    COMMENT 'Arquivos brutos baixados do portal da ANEEL'
""")

print("Volume criado ou já existente.")


# ============================================================
# 4. CRIAR PASTA NO VOLUME
# ============================================================

Path(PASTA_VOLUME_DEC_FEC).mkdir(
    parents=True,
    exist_ok=True
)

print("Pasta do Volume:", PASTA_VOLUME_DEC_FEC)


# ============================================================
# 5. SALVAR O ZIP ORIGINAL
# ============================================================

with open(CAMINHO_ZIP, "wb") as arquivo_zip_destino:
    arquivo_zip_destino.write(conteudo_download)

print("ZIP original salvo em:")
print(CAMINHO_ZIP)


# ============================================================
# 6. VALIDAR E EXTRAIR O CSV
# ============================================================

buffer_zip = io.BytesIO(conteudo_download)

if not zipfile.is_zipfile(buffer_zip):
    raise ValueError(
        "O arquivo baixado não foi reconhecido como ZIP."
    )

buffer_zip.seek(0)

with zipfile.ZipFile(buffer_zip) as arquivo_zip:

    arquivos_encontrados = arquivo_zip.namelist()

    print("Arquivos encontrados dentro do ZIP:")

    for nome_arquivo in arquivos_encontrados:
        print("-", nome_arquivo)

    arquivos_csv = [
        nome_arquivo
        for nome_arquivo in arquivos_encontrados
        if nome_arquivo.lower().endswith(".csv")
    ]

    if not arquivos_csv:
        raise ValueError(
            "Nenhum arquivo CSV foi encontrado dentro do ZIP."
        )

    nome_csv_zip = arquivos_csv[0]

    with arquivo_zip.open(nome_csv_zip) as origem:
        with open(CAMINHO_CSV, "wb") as destino:
            copyfileobj(origem, destino)

print("CSV extraído para:")
print(CAMINHO_CSV)


# ============================================================
# 7. CONFIRMAR ARQUIVOS NO VOLUME
# ============================================================

print("Arquivos existentes na pasta:")

for nome_arquivo in os.listdir(PASTA_VOLUME_DEC_FEC):
    print("-", nome_arquivo)


# ============================================================
# 8. LER O CSV COM SPARK
# ============================================================

# Validar que o arquivo existe e tem conteúdo
if not os.path.exists(CAMINHO_CSV):
    raise FileNotFoundError(
        f"Arquivo CSV não encontrado: {CAMINHO_CSV}"
    )

file_size = os.path.getsize(CAMINHO_CSV)

if file_size == 0:
    raise ValueError(
        f"Arquivo CSV está vazio: {CAMINHO_CSV}"
    )

print(f"Arquivo CSV localizado: {file_size:,} bytes")

df_dec_fec = (
    spark.read
    .option("header", True)
    .option("sep", ";")
    .option("quote", "\"")
    .option("escape", "\"")
    .option("encoding", "UTF-8")
    .csv(CAMINHO_CSV)
)

print("Schema do arquivo:")

df_dec_fec.printSchema()

print("Primeiros cinco registros:")

df_dec_fec.show(
    5,
    truncate=False
)


# ============================================================
# 9. VERIFICAR OS INDICADORES
# ============================================================

print("Indicadores encontrados:")

(
    df_dec_fec
    .select("SigIndicador")
    .distinct()
    .orderBy("SigIndicador")
    .show(100, truncate=False)
)




from pyspark.sql import functions as F

df_dec_fec_principal = (
    df_dec_fec
    .filter(F.col("SigIndicador").isin("DEC", "FEC"))
)

print("Quantidade de registros DEC e FEC:")

(
    df_dec_fec_principal
    .groupBy("SigIndicador")
    .count()
    .orderBy("SigIndicador")
    .show()
)
