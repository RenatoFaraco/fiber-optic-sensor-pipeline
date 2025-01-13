import os
import biblioteca as bib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np 


pasta_base = 'D:/DOUTORADO_RENATO/DADOS/QUEIJO/ARQUIVOS'
pasta_json = 'D:/DOUTORADO_RENATO/DADOS/QUEIJO/JSONS'
pasta_destino = 'D:/DOUTORADO_RENATO/DADOS/QUEIJO/ARQUIVOS/PARQUET'
dias = ["19_12_2024", "08_01_2025", "09_01_2025"]
rodadas_por_dia = {
    "19_12_2024": ["RODADA_1", "RODADA_2"],
    "08_01_2025": ["RODADA_1", "RODADA_2"],
    "09_01_2025": ["RODADA_1", "RODADA_2"]
}
samples = ["21104_A1", "21104_A2", "21104_A3", "21104_A4", "21104_A5"]

dados = {}

for dia in dias:
    dados[dia] = {}
    for sample in samples:
        dados[dia][sample] = {}
        for rodada in rodadas_por_dia[dia]:
            caminho = os.path.join(pasta_base, dia, rodada, sample)
            if os.path.exists(caminho):
                dados[dia][sample][rodada] = bib.ler_multiplos_txt(caminho)
                print(f"Rodada '{rodada}' para o dia '{dia}' na amostra '{sample}, processada com sucesso!'.")
            else:
                print(f"Rodada '{rodada}' não encontrada para o dia '{dia}' na amostra '{sample}'.")
                


for dia in dados:
    for sample in dados[dia]:
        for rodada in dados[dia][sample]:
            bib.plotar_dfs(dados[dia][sample][rodada])