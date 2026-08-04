from src.config import (
    CAMINHO_CSV,
    CAMINHO_ZIP,
    URL_DEC_FEC,
)


def test_url_dec_fec():
    assert URL_DEC_FEC.startswith("https://")
    assert URL_DEC_FEC.endswith(".zip")


def test_caminho_zip():
    assert CAMINHO_ZIP.startswith("/Volumes/")
    assert CAMINHO_ZIP.endswith(".zip")


def test_caminho_csv():
    assert CAMINHO_CSV.startswith("/Volumes/")
    assert CAMINHO_CSV.endswith(".csv")


def test_zip_e_csv_na_mesma_pasta():
    pasta_zip = CAMINHO_ZIP.rsplit("/", 1)[0]
    pasta_csv = CAMINHO_CSV.rsplit("/", 1)[0]

    assert pasta_zip == pasta_csv

    