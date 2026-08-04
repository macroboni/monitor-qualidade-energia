# Configurações do projeto Monitor de Qualidade de Energia

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