import os
import json
import biblioteca as bib
import pandas as pd 
import numpy as np


pasta_base = 'D:/DOUTORADO_RENATO/DADOS/QUEIJO/ARQUIVOS'
pasta_json = 'D:/DOUTORADO_RENATO/DADOS/QUEIJO/JSONS'
dias = ["19_12_2024", "08_01_2025", "09_01_2025"]
rodadas_por_dia = {
    "19_12_2024": ["RODADA_1", "RODADA_2"],
    "08_01_2025": ["RODADA_1", "RODADA_2"],
    "09_01_2025": ["RODADA_1", "RODADA_2"]
}
samples = ["21104_A1", "21104_A2", "21104_A3", "21104_A4", "21104_A5"]

dados = {}
franjas = {}

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



for dia in dias:
    franjas[dia] = {}  # Inicializa a estrutura para franjas médias
    for sample in samples:
        franjas[dia][sample] = {}  # Inicializa a estrutura para franjas médias da amostra
        for rodada in rodadas_por_dia[dia]:
                franjas[dia][sample][rodada] = bib.varre_dados(dados[dia][sample][rodada]) 
                
            
# Salvar franjas em arquivos JSON
for dia in franjas.keys():
    for sample in samples:
        for rodada in rodadas_por_dia[dia]:
            nome_arquivo_json = f"franjas_{dia}_{sample}_{rodada}.json"  # Nome do arquivo
            caminho_json = os.path.join(pasta_json, nome_arquivo_json)
            # Converte o array em lista antes de salvar
            franjas_lista = franjas[dia][sample][rodada].tolist() if isinstance(franjas[dia][sample][rodada], np.ndarray) else franjas[dia][sample][rodada]
            # Salva as franjas em formato JSON
            with open(caminho_json, 'w') as outfile:
                json.dump(franjas_lista, outfile, indent=4)
            print(f"Franjas salvas em: {caminho_json}")