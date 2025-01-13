import os
import biblioteca as bib
import pandas as pd 

pasta_base = 'D:/DOUTORADO_RENATO/DADOS/QUEIJO/ARQUIVOS'
pasta_csv = 'D:/DOUTORADO_RENATO/DADOS/QUEIJO/CSVS'  
pasta_destino = 'D:/DOUTORADO_RENATO/DADOS/QUEIJO/ARQUIVOS/PARQUET'
dias = ["19_12_2024", "08_01_2025", "09_01_2025"]
rodadas_por_dia = {
    "19_12_2024": ["RODADA_1", "RODADA_2"],
    "08_01_2025": ["RODADA_1", "RODADA_2"],
    "09_01_2025": ["RODADA_1", "RODADA_2"]
}
samples = ["21104_A1", "21104_A2", "21104_A3", "21104_A4", "21104_A5"]


dados = {}

# Cria a pasta CSV caso não exista
os.makedirs(pasta_csv, exist_ok=True)

for dia in dias:
    dados[dia] = {}
    for sample in samples:
        dados[dia][sample] = {}
        for rodada in rodadas_por_dia[dia]:
            caminho = os.path.join(pasta_base, dia, rodada, sample)
            if os.path.exists(caminho):
                # Lê os dados e assume que retorna uma lista de DataFrames
                lista_dfs = bib.ler_multiplos_txt(caminho)
                
                # Concatena a lista de DataFrames em um único DataFrame
                df = pd.concat(lista_dfs, ignore_index=True)
                
                dados[dia][sample][rodada] = df
                print(f"Rodada '{rodada}' para o dia '{dia}' na amostra '{sample}' processada com sucesso!")

                # Salva o DataFrame em um arquivo CSV
                nome_arquivo_csv = f"dados_{dia}_{sample}_{rodada}.csv"
                caminho_csv = os.path.join(pasta_csv, nome_arquivo_csv)

                # Salva o DataFrame como CSV
                df.to_csv(caminho_csv, index=False)
                print(f"Arquivo CSV '{nome_arquivo_csv}' salvo com sucesso em: {caminho_csv}")

            else:
                print(f"Rodada '{rodada}' não encontrada para o dia '{dia}' na amostra '{sample}'.")
